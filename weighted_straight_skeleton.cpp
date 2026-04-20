#include <iostream>
#include <vector>
#include <string>
#include <cstdio>
#include <stdexcept>
#include <cstring>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/extrude_skeleton.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/exceptions.h>

#ifdef _WIN64
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef Kernel::FT FT;
typedef Kernel::Point_2 Point_2;
typedef CGAL::Polygon_2<Kernel> Polygon_2;
typedef std::vector<Point_2> PointList;
typedef CGAL::General_polygon_with_holes_2<Polygon_2> Polygon_with_holes_2;
typedef Kernel::Point_3 Point_3;
typedef CGAL::Surface_mesh<Point_3> Surface_mesh;
typedef std::vector<std::vector<FT>> Angles_Matrix;

// Configure CGAL to throw exceptions instead of calling abort()
void configure_cgal_error_handling() {
    CGAL::set_error_behaviour(CGAL::THROW_EXCEPTION);
}

// Safely writes an error message into the Python-allocated error buffer
void set_error(char* buffer, std::size_t size, const std::string& message) {
    if (buffer && size > 0) {
        snprintf(buffer, size, "%s", message.c_str());
    }
}

void printPolygon(const Polygon_2& polygon) {
    std::cout << "Polygon with " << polygon.size() << " vertices:" << std::endl;
    std::cout << "[ ";
    for (auto vit = polygon.vertices_begin(); vit != polygon.vertices_end(); ++vit) {
        const Point_2& point = *vit;
        std::cout << "(" << point.x() << ", " << point.y() << ") ";
    }
    std::cout << "]" << std::endl;
}

void printAngles(const Angles_Matrix& angleMatrix) {
    for (size_t i = 0; i < angleMatrix.size(); ++i) {
        std::cout << "Angles at position " << i << ": [ ";
        for (size_t j = 0; j < angleMatrix[i].size(); ++j) {
            std::cout << angleMatrix[i][j];
            if (j < angleMatrix[i].size() - 1) std::cout << ", ";
        }
        std::cout << " ]" << std::endl;
    }
}

void printDetails(const Polygon_2& polygon, const Angles_Matrix& angle_matrix, bool success) {
    printPolygon(polygon);
    printAngles(angle_matrix);
    std::cout << "Weighted straight skeleton " << (success ? "succeeded" : "failed") << std::endl;
}

Polygon_2 create_polygon(const std::vector<double>& points, std::size_t points_cols) {
    PointList point_list;
    for (std::size_t i = 0; i < points.size(); i += points_cols) {
        point_list.push_back(Point_2(points[i], points[i + 1]));
    }
    return Polygon_2(point_list.begin(), point_list.end());
}

std::vector<FT> extract_angles(const double* angles, std::size_t contour_size) {
    return std::vector<FT>(angles, angles + contour_size);
}

extern "C" EXPORT bool compute_straight_skeleton_with_holes_and_save(
    const double* points,
    const double* holes,
    const double* angles,
    std::size_t points_rows,
    std::size_t points_cols,
    const int* holes_rows,
    const int* holes_cols,
    std::size_t holes_number,
    const char* output_file_path,
    const bool verbose,
    char* error_log,
    std::size_t buffer_size
) {
    if (error_log && buffer_size > 0) error_log[0] = '\0';

    if (!points || !angles || !output_file_path) {
        set_error(error_log, buffer_size, "Null pointer argument received in C++.");
        return false;
    }

    try {
        configure_cgal_error_handling();

        Polygon_2 polygon = create_polygon(std::vector<double>(points, points + points_rows * points_cols), points_cols);

        if (!polygon.is_simple()) {
            set_error(error_log, buffer_size, "Input outer polygon is not simple (self-intersection detected).");
            return false;
        }

        std::vector<Polygon_2> hole_polygons;
        std::size_t holes_offset = 0;
        for (std::size_t i = 0; i < holes_number; ++i) {
            int hole_point_length = holes_rows[i] * holes_cols[i];
            std::vector<double> hole(holes + holes_offset, holes + holes_offset + hole_point_length);
            Polygon_2 hole_poly = create_polygon(hole, holes_cols[i]);

            if (!hole_poly.is_simple()) {
                set_error(error_log, buffer_size, "Hole " + std::to_string(i) + " is not simple.");
                return false;
            }

            hole_polygons.push_back(hole_poly);
            holes_offset += hole_point_length;
        }

        Polygon_with_holes_2 polygon_with_holes(polygon, hole_polygons.begin(), hole_polygons.end());

        // Build angle matrix: one entry per contour (outer + holes), advancing pointer accordingly
        Angles_Matrix angle_matrix;
        const double* current_angles_ptr = angles;
        std::vector<std::size_t> contour_sizes = {points_rows};
        for (size_t i = 0; i < holes_number; ++i) contour_sizes.push_back(holes_rows[i]);

        for (auto size : contour_sizes) {
            angle_matrix.push_back(extract_angles(current_angles_ptr, size));
            current_angles_ptr += size;
        }

        auto params = CGAL::parameters::angles(angle_matrix);
        Surface_mesh out_mesh;
        bool success = CGAL::extrude_skeleton(polygon_with_holes, out_mesh, params);

        if (success) {
            CGAL::IO::write_polygon_mesh(output_file_path, out_mesh, CGAL::parameters::stream_precision(17));
        } else {
            set_error(error_log, buffer_size, "CGAL::extrude_skeleton returned false (construction failed logically).");
        }

        if (verbose) printDetails(polygon, angle_matrix, success);
        return success;

    } catch (const CGAL::Failure_exception& e) {
        set_error(error_log, buffer_size, "CGAL Geometry Error: " + std::string(e.what()));
        return false;
    } catch (const std::exception& e) {
        set_error(error_log, buffer_size, e.what());
        return false;
    } catch (...) {
        set_error(error_log, buffer_size, "Unknown fatal error occurred in C++ extension.");
        return false;
    }
}

extern "C" EXPORT bool compute_straight_skeleton_and_save(
    const double* points,
    const double* angles,
    std::size_t points_rows,
    std::size_t points_cols,
    const char* output_file_path,
    const bool verbose,
    char* error_log,
    std::size_t buffer_size
) {
    if (error_log && buffer_size > 0) error_log[0] = '\0';

    if (!points || !angles || !output_file_path) {
        set_error(error_log, buffer_size, "Null pointer argument received in C++.");
        return false;
    }

    try {
        configure_cgal_error_handling();

        Polygon_2 polygon = create_polygon(std::vector<double>(points, points + points_rows * points_cols), points_cols);

        if (!polygon.is_simple()) {
            set_error(error_log, buffer_size, "Input polygon is not simple (self-intersection detected).");
            return false;
        }

        Angles_Matrix angle_matrix;
        angle_matrix.push_back(extract_angles(angles, points_rows));

        auto params = CGAL::parameters::angles(angle_matrix);
        Surface_mesh out_mesh;
        bool success = CGAL::extrude_skeleton(polygon, out_mesh, params);

        if (success) {
            CGAL::IO::write_polygon_mesh(output_file_path, out_mesh, CGAL::parameters::stream_precision(17));
        } else {
            set_error(error_log, buffer_size, "CGAL::extrude_skeleton returned false.");
        }

        if (verbose) printDetails(polygon, angle_matrix, success);
        return success;

    } catch (const CGAL::Failure_exception& e) {
        set_error(error_log, buffer_size, "CGAL Geometry Error: " + std::string(e.what()));
        return false;
    } catch (const std::exception& e) {
        set_error(error_log, buffer_size, e.what());
        return false;
    } catch (...) {
        set_error(error_log, buffer_size, "Unknown fatal error in C++ extension.");
        return false;
    }
}