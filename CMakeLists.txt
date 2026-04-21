cmake_minimum_required(VERSION 3.10)
project(WeightedStraightSkeletonWrapper)

if(WIN32)
    # Set the CGAL data directory
    set(CGAL_DIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/CGAL-5.6.2/)
    set(GMP_LIBRARIES $ENV{WSS_PROJECT_ROOT}/dependencies/libs/CGAL-5.6.2/auxiliary/gmp/lib/)
    set(GMP_INCLUDE_DIRS $ENV{WSS_PROJECT_ROOT}/dependencies/libs/CGAL-5.6.2/auxiliary/gmp/include/)
    set(BOOST_INCLUDEDIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/boost_1_71_0/)
    set(BOOST_LIBRARYDIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/boost_1_71_0/lib64-msvc-14.0/)
endif()

if(UNIX)
    # Set the CGAL data directory
    set(CGAL_DIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/CGAL-5.6.2/)
    set(GMP_INCLUDE_DIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/gmp-6.3.0/)
    set(GMP_LIBRARIES $ENV{WSS_PROJECT_ROOT}/dependencies/libs/gmp-6.3.0/.libs/libgmp.so)
    set(MPFR_INCLUDE_DIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/mpfr-4.2.1/src/)
    set(MPFR_LIBRARIES $ENV{WSS_PROJECT_ROOT}/dependencies/libs/mpfr-4.2.1/src/.libs/libmpfr.so)
    set(BOOST_INCLUDEDIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/boost_1_71_0/)
    set(BOOST_LIBRARYDIR $ENV{WSS_PROJECT_ROOT}/dependencies/libs/boost_1_71_0/libs/)
    #set(CMAKE_MODULE_PATH $ENV{WSS_PROJECT_ROOT}/dependencies/libs/CGAL-5.6.2/cmake/modules/)
endif()


# Find required packages
find_package(CGAL REQUIRED)
find_package(Boost REQUIRED)
find_package(GMP REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

# Create the library
add_library(weighted_straight_skeleton SHARED weighted_straight_skeleton.cpp)

if(UNIX)
    target_include_directories(weighted_straight_skeleton PRIVATE ${GMP_INCLUDE_DIR} ${MPFR_INCLUDE_DIR})
endif()

# Link the library with the required packages
target_link_libraries(weighted_straight_skeleton PRIVATE ${CGAL_LIBRARIES} ${Boost_LIBRARIES} ${GMP_LIBRARIES} ${MPFR_LIBRARIES} Python3::Python)