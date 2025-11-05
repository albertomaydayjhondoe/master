#!/bin/bash
# 🔐 Neural Forge - Secrets Management Script
# ===========================================
# Safely manage API keys and sensitive configuration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SECRETS_DIR="config/secrets"
SECRETS_FILE="$SECRETS_DIR/secrets.env"
TEMPLATE_FILE="$SECRETS_DIR/secrets.env.template"

show_help() {
    echo -e "${BLUE}🔐 Neural Forge - Secrets Manager${NC}"
    echo "================================="
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}setup${NC}        Create secrets file from template"
    echo -e "  ${GREEN}validate${NC}     Check if all secrets are configured"
    echo -e "  ${GREEN}encrypt${NC}      Encrypt secrets file"
    echo -e "  ${GREEN}decrypt${NC}      Decrypt secrets file"
    echo -e "  ${GREEN}rotate${NC}       Generate new random secrets"
    echo -e "  ${GREEN}backup${NC}       Create encrypted backup"
    echo -e "  ${GREEN}restore${NC}      Restore from backup"
    echo ""
}

setup_secrets() {
    echo -e "${BLUE}🔧 Setting up secrets configuration...${NC}"
    
    # Create secrets directory
    mkdir -p "$SECRETS_DIR"
    
    if [ -f "$SECRETS_FILE" ]; then
        echo -e "${YELLOW}⚠️  Secrets file already exists${NC}"
        echo -e "${YELLOW}Do you want to overwrite it? (y/N)${NC}"
        read -r OVERWRITE
        if [ "$OVERWRITE" != "y" ] && [ "$OVERWRITE" != "Y" ]; then
            echo "Keeping existing secrets file"
            return
        fi
    fi
    
    # Copy template
    cp "$TEMPLATE_FILE" "$SECRETS_FILE"
    
    # Set secure permissions
    chmod 600 "$SECRETS_FILE"
    
    echo -e "${GREEN}✅ Secrets file created: $SECRETS_FILE${NC}"
    echo -e "${YELLOW}⚠️  Please edit this file with your real API keys${NC}"
    echo -e "${YELLOW}⚠️  Never commit real secrets to git!${NC}"
}

validate_secrets() {
    echo -e "${BLUE}🔍 Validating secrets configuration...${NC}"
    
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}❌ Secrets file not found: $SECRETS_FILE${NC}"
        echo "Run: $0 setup"
        return 1
    fi
    
    # Check for template values
    TEMPLATE_VALUES=(
        "your_meta_access_token_here"
        "your_youtube_api_key_here"
        "your_openai_api_key_here"
        "your_gologin_api_token_here"
    )
    
    ISSUES_FOUND=0
    
    for template_value in "${TEMPLATE_VALUES[@]}"; do
        if grep -q "$template_value" "$SECRETS_FILE"; then
            echo -e "${RED}❌ Template value found: $template_value${NC}"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    done
    
    # Check for empty values
    EMPTY_VALUES=$(grep -c "=your_\|=$" "$SECRETS_FILE" || true)
    if [ "$EMPTY_VALUES" -gt 0 ]; then
        echo -e "${RED}❌ Empty or template values found: $EMPTY_VALUES${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + EMPTY_VALUES))
    fi
    
    if [ "$ISSUES_FOUND" -eq 0 ]; then
        echo -e "${GREEN}✅ All secrets appear to be configured${NC}"
        return 0
    else
        echo -e "${RED}❌ Found $ISSUES_FOUND issues with secrets configuration${NC}"
        return 1
    fi
}

rotate_secrets() {
    echo -e "${BLUE}🔄 Rotating random secrets...${NC}"
    
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}❌ Secrets file not found${NC}"
        return 1
    fi
    
    # Generate new random secrets
    NEW_DB_KEY=$(openssl rand -hex 32)
    NEW_JWT_SECRET=$(openssl rand -hex 32)
    
    # Update secrets file
    sed -i.bak "s/DATABASE_ENCRYPTION_KEY=.*/DATABASE_ENCRYPTION_KEY=$NEW_DB_KEY/" "$SECRETS_FILE"
    sed -i.bak "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$NEW_JWT_SECRET/" "$SECRETS_FILE"
    
    echo -e "${GREEN}✅ Random secrets rotated${NC}"
    echo -e "${YELLOW}⚠️  Backup created: $SECRETS_FILE.bak${NC}"
}

encrypt_secrets() {
    echo -e "${BLUE}🔒 Encrypting secrets file...${NC}"
    
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}❌ Secrets file not found${NC}"
        return 1
    fi
    
    echo "Enter encryption password:"
    read -s PASSWORD
    
    # Encrypt with AES-256
    openssl enc -aes-256-cbc -salt -in "$SECRETS_FILE" -out "$SECRETS_FILE.enc" -pass pass:"$PASSWORD"
    
    echo -e "${GREEN}✅ Secrets encrypted: $SECRETS_FILE.enc${NC}"
    echo -e "${YELLOW}⚠️  Store the password securely!${NC}"
}

decrypt_secrets() {
    echo -e "${BLUE}🔓 Decrypting secrets file...${NC}"
    
    if [ ! -f "$SECRETS_FILE.enc" ]; then
        echo -e "${RED}❌ Encrypted secrets file not found${NC}"
        return 1
    fi
    
    echo "Enter decryption password:"
    read -s PASSWORD
    
    # Decrypt
    openssl enc -aes-256-cbc -d -in "$SECRETS_FILE.enc" -out "$SECRETS_FILE" -pass pass:"$PASSWORD"
    
    if [ $? -eq 0 ]; then
        chmod 600 "$SECRETS_FILE"
        echo -e "${GREEN}✅ Secrets decrypted successfully${NC}"
    else
        echo -e "${RED}❌ Decryption failed - wrong password?${NC}"
        return 1
    fi
}

backup_secrets() {
    echo -e "${BLUE}💾 Creating encrypted backup...${NC}"
    
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${RED}❌ Secrets file not found${NC}"
        return 1
    fi
    
    BACKUP_NAME="secrets_backup_$(date +%Y%m%d_%H%M%S).enc"
    
    echo "Enter backup encryption password:"
    read -s PASSWORD
    
    openssl enc -aes-256-cbc -salt -in "$SECRETS_FILE" -out "$SECRETS_DIR/$BACKUP_NAME" -pass pass:"$PASSWORD"
    
    echo -e "${GREEN}✅ Backup created: $BACKUP_NAME${NC}"
}

# Main command handler
case "$1" in
    setup)
        setup_secrets
        ;;
    validate)
        validate_secrets
        ;;
    rotate)
        rotate_secrets
        ;;
    encrypt)
        encrypt_secrets
        ;;
    decrypt)
        decrypt_secrets
        ;;
    backup)
        backup_secrets
        ;;
    restore)
        echo "Restore functionality would be implemented here"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            show_status
        else
            echo -e "${RED}❌ Unknown command: $1${NC}"
            show_help
            exit 1
        fi
        ;;
esac