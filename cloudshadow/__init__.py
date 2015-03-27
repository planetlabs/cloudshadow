
import numpy as np
from scipy import ndimage
import raster as rio


def get_spherical_azimuth(az):
    """
    Convert the Landsat defined azimuth to the spherical coordinate
    convention used in physics.
    
    :param az:
    """
    # Flip across y-axis, offset, and convert
    # domain from [-180, +180] to [0, 360]
    azimuth = (-1 * az + 90) % 360
    
    return azimuth
    
    
def get_spherical_zenith(ze):
    """
    Convert the Landsat defined zenith to the spherical coordinate
    convention used in physics.
    
    :param ze:
    """
    # Translate angle and convert domain
    # from [-90, +90] to [0, 180]
    zenith = (-ze + 90) % 180

    return zenith


def get_xyz(az, ze):
    """
    Convert from spherical coordinates to cartesian. A fixed radius is assumed.
    
    :param az:
        Azimuth angle in degrees
    :param ze:
        Zenith angle in degrees
    """
    
    # Convert to radians
    azimuth = az * np.pi / 180.
    zenith = ze * np.pi / 180.
    
    x = np.sin(zenith) * np.cos(azimuth)
    y = np.sin(zenith) * np.sin(azimuth)
    z = np.cos(zenith)
    
    return (x, y, z)


def get_xy_intersection(p0, p1):
    """
    Get the intersection of a 3D vector with the xy plane.
    
    :param p0:
        Three dimensional vector (numpy array)
    :param p1:
        Three dimensional vector (numpy array)
    """
    l = p1 - p0
    zn = np.array([0, 0, 1])
    return p0 + np.dot(zn, p0) / np.dot(zn, -1*l) * l


def to_pixel_space(x, y, width, height):
    """
    Convert from unit coordinates to pixel coordinates.
    
    :param x:
        Transform from [-1, 1] to [0, image width]
    :param y:
        Transform from [-1, 1] to [0, image height]
    """
    xp = (x + 1) * 0.5 * width
    yp = (-1 * y + 1) * 0.5 * height
    
    return (xp, yp)
    

def get_cloud_shadows(srcpath, sun_azimuth, sun_elevation, dstpath):
    """
    :param srcpath:
    :param sun_azimuth:
    
        Sun azimuth angle (degrees) at the WRS scene center. A positive
        value (+) indicates angles to the East or clockwise from North.
        Zero indicates North. A negative value (-) indicates angles to
        the West or counterclockwise from North.
        
        -180 through +180 degrees
        
    :param sun_elevation:
    
        Sun elevation angle (degrees) at the WRS scene center. A positive
        value (+) indicates a daytime scene. Zero indicates a nighttime
        scene. A negative value (-) indicates a nighttime scene.
        
        -90 through +90 degrees
    
    :param dstpath:
    """
    
    with rio.drivers():
        with rio.open(srcpath, 'r') as src:
            cmask = src.read_band(1)
    
    # Label the cloud mask and get the 1st moment
    lbl, n_features = ndimage.label(band)
    centroids = ndimage.measurements.center_of_mass(band, lbl, [i for i in xrange(1, n_features - 1)])
    
    # Transform Landsat defined sun position into spherical coordinates
    # TODO: Generalize with decorator since not all imagery will be Landsat
    azimuth = get_spherical_azimuth(sun_azimuth)
    zenith = get_spherical_zenith(sun_elevation)
    
    # Get cartesian coordinates for the sun
    # This assumes the sun is at r = 1
    x_sun, y_sun, z_sun = get_xyz(sun_azimuth, sun_elevation)
    
    # Assume the cloud is half way between the sun and ground
    # TODO: Improve this approximation
    #       or walk along line of shadow to sample pixels
    cloud_altitude = 0.05 * z_sun
    
    height, width = cmask.shape
    xp_sun, yp_sun = to_pixel_space(x_sun, y_sun, width, height)
    
    # TODO: Generalize to all centroids
    p0 = np.array([xp_sun, yp_sun, z_sun])
    p1 = np.array([centroids[0][0], centroids[0][1], cloud_altitude])
    
    # Get the intersection of the ray with the ground
    x_intersect, y_intersect, z_intersect = get_xy_intersection(p0, p1)
    
    # TODO: Sample the pixel at (x_intersect, y_intersect)
    
    
    
    
    
    
    
    
    
    