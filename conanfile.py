#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from conan import ConanFile
from conan.tools.files import get
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.env import VirtualBuildEnv
import json

required_conan_version = ">=2.0"


class RegxmlLibConan(ConanFile):

    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = []
    tool_requires = ["cmake/[>=3.21.1]", "ninja/[>=1.11.1]"]
    # ---Sources---
    exports = ["info.json"]
    exports_sources = []
    # ---Binary model---
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    def validate(self):
        valid_os = ["Windows", "Linux", "Macos"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")
        valid_arch = ["x86_64", "armv8"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")
        if str(self.settings.os) == 'Windows' and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} does not support building shared library on Windows")

    def requirements(self):
        self.requires("xerces-c/[>=3.2.5]", options={"network": False, "shared": False})

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, url="https://github.com/sandflow/regxmllib/archive/refs/tags/%s.zip" % self.version, strip_root=True)

        f = open("CMakeLists.txt", "w")
        f.write("""
cmake_minimum_required (VERSION 3.5)
project (regxmllibc)

find_package(XercesC REQUIRED)
include_directories(src/main/cpp)

file(GLOB_RECURSE SRC_FILES src/main/cpp/*.cpp src/main/cpp/*.h )
add_library(${PROJECT_NAME} ${SRC_FILES})
install(TARGETS ${PROJECT_NAME} LIBRARY DESTINATION lib ARCHIVE DESTINATION lib)

target_link_libraries ( ${PROJECT_NAME} PRIVATE XercesC::XercesC )

install(DIRECTORY src/main/cpp/com DESTINATION include FILES_MATCHING PATTERN "*.h")
        """)
        f.close()

    def configure(self):
        if not self.options.shared:
            self.options.rm_safe("fPIC")

    def generate(self):
        VirtualBuildEnv(self).generate()
        CMakeDeps(self).generate()
        tc = CMakeToolchain(self, generator="Ninja")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["regxmllibc"]
        self.cpp_info.bindirs = []
