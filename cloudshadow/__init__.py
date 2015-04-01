
import numpy as np
from scipy import ndimage
import rasterio as rio


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
    Get the intersection of a 3D vector with the xy plane,
    e.g., the vector between a sun and cloud projected to the ground.
    
    :param p0:
        Three dimensional vector (numpy array)
    :param p1:
        Three dimensional vector (numpy array)
    """
    l = np.rot90(p1 - p0, k=-1)
    zn = np.array([0, 0, 1])
    
    tmp = np.array([p0]).T + np.dot(zn, p0) / np.dot(zn, -1*l) * l
    return np.rot90(tmp, k=1)


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
            band = src.read(1)
    
    # Transform the sun azimuth angle
    azimuth = get_spherical_azimuth(sun_azimuth)
    azimuth += 90
    azimuth_radians = azimuth * np.pi / 180.0
    
    unit_offset = np.array([np.sin(azimuth_radians), np.cos(azimuth_radians)])
    
    # Label the cloud mask and get the 1st moment
    lbl, n_features = ndimage.label(band)
    centroids = np.array(ndimage.measurements.center_of_mass(band, lbl, np.arange(1, n_features - 1)))
    n_centroids = len(centroids)
    
    print type(centroids)
    centroid_offsets = 100 * unit_offset + centroids
    
    # Get points between the centroids and offsets
    m = np.divide.reduce(unit_offset)
    
    # Generate the domain for each vector projected in the direction
    # of the cast shadow
    x0 = centroids[:, 1].reshape(-1, 1)
    x1 = centroid_offsets[:, 1].reshape(-1, 1)
    steps = np.linspace(0, 1, 100)
    x = x0 + (x1 - x0) * steps
    
    # Get the y component of the projected vector
    y0 = centroids[:, 0].reshape(-1, 1)
    y = m * (x - x0) + y0
    
    return (x, y)
    
    # Transform Landsat defined sun position into spherical coordinates
    # TODO: Generalize with decorator since not all imagery will be Landsat
    azimuth = get_spherical_azimuth(sun_azimuth)
    zenith = get_spherical_zenith(sun_elevation)
    
    # Get cartesian coordinates for the sun
    # This assumes the sun is at r = 1
    x_sun, y_sun, z_sun = get_xyz(sun_azimuth, sun_elevation)
    
    # Choose two extremes for cloud elevation
    # TODO: Parameterize based on thermal response
    min_cloud_ele = 0 * z_sun
    max_cloud_ele = 0.5 * z_sun
    
    height, width = band.shape
    xp_sun, yp_sun = to_pixel_space(x_sun, y_sun, width, height)
    
    sun_vector = np.array([xp_sun, yp_sun, z_sun])
    
    min_ele_cloud_vectors = np.append(centroids, min_cloud_ele * np.ones((n_centroids, 1)), 1)
    max_ele_cloud_vectors = np.append(centroids, max_cloud_ele * np.ones((n_centroids, 1)), 1)
    
    # Get the intersection of the ray with the ground
    min_cloud_ele_intersects = get_xy_intersection(sun_vector, min_ele_cloud_vectors)
    max_cloud_ele_intersects = get_xy_intersection(sun_vector, max_ele_cloud_vectors)
    
    # Sample points along the projected line containing the cloud shadow
    
    return {
        'sun': sun_vector,
        'min_cloud_ele': min_cloud_ele_intersects,
        'max_cloud_ele': max_cloud_ele_intersects
    }
    