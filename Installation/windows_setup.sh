echo "===Windows Environment Setup + Check==="



#1.1: Check Python Installation On PATH
PYTHON=$(cmd.exe /c "where python" | tr -d '\r' | head -n 1)

if [ -z "$PYTHON" ]; then
    echo "(ERROR) Python Installation Not Found On System PATH"
    exit 1
fi

#1.2: Check Python Version
PY_VERSION=$(cmd.exe /c "$PYTHON --version" 2>&1 | tr -d '\r')

if [ $? -eq 0 ]; then
    MAJOR=$(echo "$PY_VERSION" | awk -F'[ .]' '{print $2}')
    MINOR=$(echo "$PY_VERSION" | awk -F'[ .]' '{print $3}')
    if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]; }; then
        echo "(ERROR): Please Utilize Python Version 3.10+. Current: $MAJOR.$MINOR"
        exit 1
    else
        echo "--Accepted Python Version (3.10+). Found: $MAJOR.$MINOR"
    fi
else
    echo "(ERROR) Unable To Extract Python Version"
    exit 1
fi


#2: Check Pip Installation + Version
PIP_VERSION=$(cmd.exe /c "$PYTHON -m pip --version" 2>&1 | tr -d '\r')

if [[ "$PIP_VERSION" == *"pip "* ]]; then 
    MAJOR=$(echo "$PIP_VERSION" | awk -F'[ .]' '{print $2}')
    MINOR=$(echo "$PIP_VERSION" | awk -F'[ .]' '{print $3}')
    if [ "$MAJOR" -lt 23 ]; then
        echo "(ERROR): Please Utilize Pip Version (23.0+). Found: $MAJOR.$MINOR"
        exit 1
    else
        echo "--Accepted Pip    Version (23.0+). Found: $MAJOR.$MINOR"
    fi
else
    echo "(ERROR): Pip Not Found Within Executable."
    exit 1
fi


#3: Install Required Packages

#TODO: MORE TO MORE GENERIC LOCATION
PACKAGES=(
    "numpy==1.26.0"
    "pandas==2.1.0"
    "scikit-learn==1.3.0"
    "matplotlib==3.8.0"
)

for pkg in "${PACKAGES[@]}"; do
    cmd.exe /c "$PYTHON -m pip install $pkg -qq"
    if [ $? -ne 0 ]; then
        echo "(ERROR): Failed To Install Package: $pkg"
        exit 1
    else
        echo "--Installed Package: $pkg"
    fi
done