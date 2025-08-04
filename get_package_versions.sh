#!/bin/bash

echo "🔍 Extracting package versions from pyproject.toml..."
echo "=================================================="

# Extract package names from pyproject.toml dependencies
echo "📦 Core Dependencies:"
echo "---------------------"

# Extract dependencies and check versions
dependencies=(
    "numpy"
    "fastapi"
    "openai"
    "scholarly"
    "functions-framework"
    "requests"
    "firebase_admin"
    "google-cloud-firestore"
    "mongoengine"
    "pymongo"
    "google-cloud-secret-manager"
    "langchain"
    "langchain-community"
    "langchain-openai"
    "langchain-core"
    "langsmith"
    "langgraph"
    "qdrant_client"
    "langchain_qdrant"
    "pypdf"
    "unstructured"
    "markdown"
    "python-docx"
    "pytest"
    "pytest-asyncio"
    "tiktoken"
    "httpx"
    "anyio"
    "pydantic"
    "python-multipart"
    "uvicorn"
    "google-cloud-storage"
    "serpapi"
)

# Check each package version
for package in "${dependencies[@]}"; do
    # Handle packages with different import names
    case $package in
        "google-cloud-firestore")
            import_name="google.cloud.firestore"
            ;;
        "google-cloud-secret-manager")
            import_name="google.cloud.secret_manager"
            ;;
        "google-cloud-storage")
            import_name="google.cloud.storage"
            ;;
        "qdrant_client")
            import_name="qdrant_client"
            ;;
        "langchain_qdrant")
            import_name="langchain_qdrant"
            ;;
        "langchain-community")
            import_name="langchain_community"
            ;;
        "langchain-openai")
            import_name="langchain_openai"
            ;;
        "langchain-core")
            import_name="langchain_core"
            ;;
        "langgraph")
            import_name="langgraph"
            ;;
        "python-multipart")
            import_name="multipart"
            ;;
        "functions-framework")
            import_name="functions_framework"
            ;;
        "firebase_admin")
            import_name="firebase_admin"
            ;;
        "pytest-asyncio")
            import_name="pytest_asyncio"
            ;;
        "python-docx")
            import_name="docx"
            ;;
        "unstructured")
            import_name="unstructured"
            ;;
        *)
            import_name=$package
            ;;
    esac
    
    # Try to get version using Python with multiple methods
    version=$(python3 -c "
import sys
import importlib

def get_version(import_name, package_name):
    try:
        module = importlib.import_module(import_name)
        
        # Method 1: Direct __version__ attribute
        if hasattr(module, '__version__'):
            return module.__version__
        
        # Method 2: Try other common version attributes
        for attr in ['version', 'VERSION']:
            if hasattr(module, attr):
                return getattr(module, attr)
        
        # Method 3: Try pkg_resources
        try:
            import pkg_resources
            return pkg_resources.get_distribution(package_name).version
        except:
            pass
        
        # Method 4: Try importlib.metadata
        try:
            from importlib.metadata import version
            return version(package_name)
        except:
            pass
        
        return 'Unknown'
        
    except ImportError:
        return 'Not installed'
    except Exception as e:
        return 'Error: ' + str(e)

print(get_version('$import_name', '$package'))
" 2>/dev/null)
    
    if [ "$version" = "Not installed" ]; then
        echo "❌ $package: Not installed"
    elif [ "$version" = "Unknown" ]; then
        echo "⚠️  $package: Installed (version unknown)"
    elif [[ "$version" == Error:* ]]; then
        echo "❌ $package: $version"
    else
        echo "✅ $package: $version"
    fi
done

echo ""
echo "🔧 Development Dependencies:"
echo "---------------------------"

dev_dependencies=(
    "pytest"
    "pytest-asyncio"
    "black"
    "flake8"
    "mypy"
)

for package in "${dev_dependencies[@]}"; do
    # Handle packages with different import names for dev dependencies
    case $package in
        "pytest-asyncio")
            import_name="pytest_asyncio"
            ;;
        *)
            import_name=$package
            ;;
    esac
    
    # Try to get version using Python with multiple methods
    version=$(python3 -c "
import sys
import importlib

def get_version(import_name, package_name):
    try:
        module = importlib.import_module(import_name)
        
        # Method 1: Direct __version__ attribute
        if hasattr(module, '__version__'):
            return module.__version__
        
        # Method 2: Try other common version attributes
        for attr in ['version', 'VERSION']:
            if hasattr(module, attr):
                return getattr(module, attr)
        
        # Method 3: Try pkg_resources
        try:
            import pkg_resources
            return pkg_resources.get_distribution(package_name).version
        except:
            pass
        
        # Method 4: Try importlib.metadata
        try:
            from importlib.metadata import version
            return version(package_name)
        except:
            pass
        
        return 'Unknown'
        
    except ImportError:
        return 'Not installed'
    except Exception as e:
        return 'Error: ' + str(e)

print(get_version('$import_name', '$package'))
" 2>/dev/null)
    
    if [ "$version" = "Not installed" ]; then
        echo "❌ $package: Not installed"
    elif [ "$version" = "Unknown" ]; then
        echo "⚠️  $package: Installed (version unknown)"
    elif [[ "$version" == Error:* ]]; then
        echo "❌ $package: $version"
    else
        echo "✅ $package: $version"
    fi
done

echo ""
echo "📋 Summary:"
echo "-----------"
echo "Total packages checked: $((${#dependencies[@]} + ${#dev_dependencies[@]}))"
echo ""
echo "💡 To install missing packages:"
echo "pip install -e ."
echo ""
echo "💡 To install with dev dependencies:"
echo "pip install -e .[dev]" 