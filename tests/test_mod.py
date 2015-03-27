
from cloudshadow import *


def test_get_spherical_azimuth():
    assert get_spherical_azimuth(0) == 90
    assert get_spherical_azimuth(90) == 0
    assert get_spherical_azimuth(180) == 270
    assert get_spherical_azimuth(-180) == 270
    assert get_spherical_azimuth(-90) == 180
    assert get_spherical_azimuth(0) == 90
    

def test_get_spherical_azimuth():
    assert get_spherical_zenith(90) == 0
    assert get_spherical_zenith(0) == 90
    assert get_spherical_zenith(-89) == 179
