
from right_hand_side import RHSOperator
from tools import prims_to_cons, \
    cons_to_prims, JAx1, JAx2, JAx3


def Euler(V, dt, g, a, p):
    """
    Synopsis
    --------
    Evolve the simulation domain though dt
    using the Euler method.

    Args
    ----
    V: numpy array-like
    State vector containing the hole solution
    and all variables

    dt: double-like
    Time step, in simulation units.

    g: object-like
    Object containing all variables related to
    the grid, e.g. cell width.

    a: object-like
    object containing specified algorithms for use
    in the seprate stages of a time step.

    p: dic-like
    Dictionary of user defined ps, e.g.
    maximum simulation time.

    Attributes
    ----------
    None.

    TODO
    ----
    None
    """
    U = prims_to_cons(V, a)
    U_new = U + dt*RHSOperator(U, g, a)
    g.boundary(U_new, p)
    V = cons_to_prims(U_new, a)

    return V


def RungaKutta2(V, dt, g, a, p):
    """
    Synopsis
    --------
    Evolve the simulation domain though time dt
    using the 2nd order RK method.

    Args
    ----
    V: numpy array-like
    State vector containing the hole solution
    and all variables

    dt: double-like
    Time step, in simulation units.

    g: object-like
    Object containing all variables related to
    the grid, e.g. cell width.

    a: object-like
    object containing specified algorithms for use
    in the seprate stages of a time step.

    p: dic-like
    Dictionary of user defined ps, e.g.
    maximum simulation time.

    Attributes
    ----------
    None.

    TODO
    ----
    None
    """

    U = prims_to_cons(V, a)
    K1 = RHSOperator(U, g, a, dt)
    g.boundary(K1, p)

    # My need to recalculate the time step here.

    K2 = RHSOperator(U+K1, g, a, dt)
    U_new = U + 0.5*(K1 + K2)
    g.boundary(U_new, p)
    V = cons_to_prims(U_new, a)

    return V


def muscl_hanock(V, dt, g, a, p):
    """
    Synopsis
    --------
    Evolve the simulation domain though time dt
    using the 2nd order MUSCL-hanck method.

    Args
    ----
    V: numpy array-like
    State vector containing the hole solution
    and all variables

    dt: double-like
    Time step, in simulation units.

    g: object-like
    Object containing all variables related to
    the grid, e.g. cell width.

    a: object-like
    object containing specified algorithms for use
    in the seprate stages of a time step.

    p: dic-like
    Dictionary of user defined ps, e.g.
    maximum simulation time.

    Attributes
    ----------
    None.

    TODO
    ----
    None
    """

    dflux = RHSOperator(V, g, a, dt)

    U = prims_to_cons(V, a)
    U_new = U + dt*dflux
    V = cons_to_prims(U_new, a)

    return V
