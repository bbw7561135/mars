
import sys
import numpy as np
import numba as nb
from numba import prange
from settings import *
from tools import flux_tensor, cons_to_prims, prims_to_cons, time_step


def flux_difference(U, g, a, t, dt, vxn, vxt, vxb):
    """
    Synopsis
    --------
    Construct the fluxes through the cell
    faces normal to the direction of "axis".

    Args
    ----
    U: numpy array-like
    state vector containing all
    conservative variables.

    g: object-like
    object containing all variables related to
    the grid, e.g. cell width.

    a: object-like
    object containing specified algorithms for use
    in the seprate stages of a time step.

    vx(n,t,b): int-like
    indexes for for the normal, tangential and
    bi-tangential velocity components.

    Attributes
    ----------
    None.

    TODO
    ----
    None
    """

    V = np.empty(shape=U.shape, dtype=np.float64)
    cons_to_prims(U, V, a.gamma_1)

    t.start_reconstruction()
    VL, VR = a.reconstruction(V)
    t.stop_reconstruction()

    UL = np.empty(shape=VL.shape, dtype=np.float64)
    UR = np.empty(shape=VR.shape, dtype=np.float64)
    prims_to_cons(VL, UL, a.igamma_1)
    prims_to_cons(VR, UR, a.igamma_1)

    FL = np.empty(shape=VL.shape, dtype=np.float64)
    FR = np.empty(shape=VR.shape, dtype=np.float64)
    flux_tensor(UL, VL, FL, vxn, vxt, vxb)
    flux_tensor(UR, VR, FR, vxn, vxt, vxb)

    t.start_riemann()
    dflux, g.speed_max = a.riemann_solver(
        FL, FR, UL, UR, VL, VR,
        g.speed_max, a.gamma, dt/g.dxi[vxn-2],
        vxn, vxt, vxb
    )
    t.stop_riemann()

    return dflux


def RHSOperator(U, g, a, t, dt):
    """
    Synopsis
    --------
    Determine the right hand side operator.

    Args
    ----
    U: numpy array-like
    state vector containing all
    conservative variables.

    g: object-like
    object containing all variables related to
    the grid, e.g. cell width.

    a: object-like
    object containing specified algorithms for use
    in the seprate stages of a time step.

    Attributes
    ----------
    None.

    TODO
    ----
    None
    """

    t.start_space_loop()
    rhs = np.zeros(shape=U.shape, dtype=np.float64)

    if U.shape[0] == 3:

        rhs[:, g.ibeg:g.iend] = flux_difference(U, g, a, t, dt, vxn=2, vxt=3, vxb=4)

    if U.shape[0] == 4:

        for j in prange(g.jbeg, g.jend):
            rhs[:, j, g.ibeg:g.iend] = flux_difference(U[:, j, :], g, a, t, dt, vxn=2, vxt=3, vxb=4)

        for i in prange(g.ibeg, g.iend):
            rhs[:, g.jbeg:g.jend, i] += flux_difference(U[:, :, i], g, a, t, dt, vxn=3, vxt=2, vxb=4)

    if U.shape[0] == 5:

        for k in range(g.jbeg, g.jend):
            for j in range(g.jbeg, g.jend):
                rhs[:, k, j, g.ibeg:g.iend] = flux_difference(U[:, k, j, :], g, a, t, dt, vxn=2, vxt=3, vxb=4)

        for k in range(g.kbeg, g.kend):
            for i in range(g.ibeg, g.iend):
                rhs[:, k, g.jbeg:g.jend, i] += flux_difference(U[:, k, :, i], g, a, t, dt, vxn=3, vxt=2, vxb=4)

        for j in range(g.jbeg, g.jend):
            for i in range(g.ibeg, g.iend):
                rhs[:, g.kbeg:g.kend, j, i] += flux_difference(U[:, :, j, i], g, a, t, dt, vxn=4, vxt=2, vxb=3)
    t.stop_space_loop()

    return rhs
