#!/bin/bash

WSS_PROJECT_ROOT=$(pwd)
export WSS_PROJECT_ROOT

mkdir -p dependencies
cd dependencies

wget https://github.com/CGAL/cgal/releases/download/v5.2/CGAL-5.2.tar.xz
tar -xf CGAL-5.2.tar.xz
rm CGAL-5.2.tar.xz

wget https://github.com/CGAL/cgal/releases/download/v5.6.2/CGAL-5.6.2.tar.xz
tar -xf CGAL-5.6.2.tar.xz
rm CGAL-5.6.2.tar.xz

wget https://archives.boost.io/release/1.71.0/source/boost_1_71_0.tar.bz2
tar --bzip2 -xf boost_1_71_0.tar.bz2
rm boost_1_71_0.tar.bz2 

wget https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz
tar -xf gmp-6.3.0.tar.xz
rm gmp-6.3.0.tar.xz
cd gmp-6.3.0
./configure --enable-shared --prefix=$WSS_PROJECT_ROOT/dependencies/gmp-6.3.0
make
make check
cd ..

wget https://www.mpfr.org/mpfr-4.2.1/mpfr-4.2.1.tar.xz
tar -xf mpfr-4.2.1.tar.xz
rm mpfr-4.2.1.tar.xz
cd mpfr-4.2.1
./configure --with-gmp-lib=$WSS_PROJECT_ROOT/dependencies/gmp-6.3.0/.libs/ --with-gmp-include=$WSS_ROJECT_PROOT/dependencies/gmp-6.3.0/
make
make check
cd ../..

cmake -S ./ -B ./build -DCMAKE_BUILD_TYPE=Release
cmake --build ./build --config Release