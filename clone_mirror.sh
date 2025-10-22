#!/bin/bash
# Script to clone a mirror of the SPAYTK/master repository
# A mirror clone creates a bare repository that includes all refs and remote-tracking information

# Clone the repository as a mirror
git clone --mirror https://github.com/SPAYTK/master.git

# Navigate into the cloned mirror directory
cd master.git

echo "Mirror clone completed successfully!"
echo "This is a bare repository containing all refs and remote-tracking information."
echo ""
echo "To push this mirror to another remote, use:"
echo "  git push --mirror <remote-url>"
