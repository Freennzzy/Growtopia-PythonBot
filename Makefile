CXX = clang++

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    LIB_EXT = .so
    CXXFLAGS = -fPIC
    DEFINES = -DENET_IMPLEMENTATION
else ifeq ($(UNAME_S),Darwin)
    LIB_EXT = .dylib
    CXXFLAGS = -fPIC
    DEFINES = -DENET_IMPLEMENTATION
else
    LIB_EXT = .dll
    CXXFLAGS = 
    DEFINES = -DENET_DLL -DENET_IMPLEMENTATION
endif

LIB_NAME = enet/enet$(LIB_EXT)

all: $(LIB_NAME) requirements

requirements:
	@echo "Installing Python requirements..."
	pip install -r requirements.txt

$(LIB_NAME): enet/enet.cpp
	@echo "Compiling enet for $(UNAME_S)..."
	$(CXX) $(CXXFLAGS) enet/enet.cpp -shared $(DEFINES) -o $@