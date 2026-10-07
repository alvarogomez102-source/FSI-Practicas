"""Search (Chapters 3-4)

The way to use this code is to subclass Problem to create a class of problems,
then create problem instances and solve them with calls to the various search
functions."""


from utils import *
import random
import sys


# ______________________________________________________________________________


class Problem:
    """The abstract class for a formal problem.  You should subclass this and
    implement the method successor, and possibly __init__, goal_test, and
    path_cost. Then you will create instances of your subclass and solve them
    with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal.  Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def successor(self, state):
        """Given a state, return a sequence of (action, state) pairs reachable
        from this state. If there are many successors, consider an iterator
        that yields the successors one at a time, rather than building them
        all at once. Iterators will work fine within the framework."""
        abstract

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Implement this
        method if checking against a single self.goal is not enough."""
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        abstract


# ______________________________________________________________________________

class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        update(self, state=state, parent=parent, action=action,
               path_cost=path_cost, depth=0)
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node %s>" % (self.state,)

    def path(self):
        """Create a list of nodes from the root to this node."""
        x, result = self, [self]
        while x.parent:
            result.append(x.parent)
            x = x.parent
        return result

    def expand(self, problem):
        """Return a list of nodes reachable from this node. [Fig. 3.8]"""
        return [Node(next, self, act,
                     problem.path_cost(self.path_cost, self.state, act, next))
                for (act, next) in problem.successor(self.state)]


# ______________________________________________________________________________
## Uninformed Search algorithms

def graph_search(problem, fringe):
    """Search through the successors of a problem to find a goal.
    The argument fringe should be an empty queue.
    If two paths reach a state, only use the best one. [Fig. 3.18]"""
    closed = {}
    fringe.append(Node(problem.initial))
    while fringe:
        node = fringe.pop()
        if problem.goal_test(node.state):
            return node
        if node.state not in closed:
            closed[node.state] = True
            fringe.extend(node.expand(problem))
    return None


def breadth_first_graph_search(problem):
    """Search the shallowest nodes in the search tree first. [p 74]"""
    return graph_search(problem, FIFOQueue())  # FIFOQueue -> fringe


def depth_first_graph_search(problem):
    """Search the deepest nodes in the search tree first. [p 74]"""
    return graph_search(problem, Stack())


def branch_and_bound_graph_search(problem):
    """Expand the node with the lowest accumulated path cost first."""
    return graph_search(problem, BranchAndBoundQueue())


def branch_and_bound_h_graph_search(problem):
    """Expand the node with the lowest path cost + heuristic first."""
    return graph_search(problem, BranchAndBoundHQueue(problem))
# _____________________________________________________________________________
# The remainder of this file implements examples for the search algorithms.

# ______________________________________________________________________________
# Graphs and Graph Problems

class Graph:
    """A graph connects nodes (vertices) by edges (links).  Each edge can also
    have a length associated with it.  The constructor call is something like:
        g = Graph({'A': {'B': 1, 'C': 2})
    this makes a graph with 3 nodes, A, B, and C, with an edge of length 1 from
    A to B,  and an edge of length 2 from A to C.  You can also do:
        g = Graph({'A': {'B': 1, 'C': 2}, directed=False)
    This makes an undirected graph, so inverse links are also added. The graph
    stays undirected; if you add more links with g.connect('B', 'C', 3), then
    inverse link is also added.  You can use g.nodes() to get a list of nodes,
    g.get('A') to get a dict of links out of A, and g.get('A', 'B') to get the
    length of the link from A to B.  'Lengths' can actually be any object at
    all, and nodes can be any hashable object."""

    def __init__(self, dict=None, directed=True):
        self.dict = dict or {}
        self.directed = directed
        if not directed:
            self.make_undirected()

    def make_undirected(self):
        """Make a digraph into an undirected graph by adding symmetric edges."""
        for a in list(self.dict.keys()):
            for (b, distance) in list(self.dict[a].items()):
                self.connect1(b, a, distance)

    def connect(self, A, B, distance=1):
        """Add a link from A and B of given distance, and also add the inverse
        link if the graph is undirected."""
        self.connect1(A, B, distance)
        if not self.directed: self.connect1(B, A, distance)

    def connect1(self, A, B, distance):
        """Add a link from A to B of given distance, in one direction only."""
        self.dict.setdefault(A, {})[B] = distance

    def get(self, a, b=None):
        """Return a link distance or a dict of {node: distance} entries.
        .get(a,b) returns the distance or None;
        .get(a) returns a dict of {node: distance} entries, possibly {}."""
        links = self.dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)

    def nodes(self):
        """Return a list of nodes in the graph."""
        return list(self.dict.keys())


def UndirectedGraph(dict=None):
    """Build a Graph where every edge (including future ones) goes both ways."""
    return Graph(dict=dict, directed=False)


def RandomGraph(nodes=list(range(10)), min_links=2, width=400, height=300,
                curvature=lambda: random.uniform(1.1, 1.5)):
    """Construct a random graph, with the specified nodes, and random links.
    The nodes are laid out randomly on a (width x height) rectangle.
    Then each node is connected to the min_links nearest neighbors.
    Because inverse links are added, some nodes will have more connections.
    The distance between nodes is the hypotenuse times curvature(),
    where curvature() defaults to a random number between 1.1 and 1.5."""
    g = UndirectedGraph()
    g.locations = {}
    ## Build the cities
    for node in nodes:
        g.locations[node] = (random.randrange(width), random.randrange(height))
    ## Build roads from each city to at least min_links nearest neighbors.
    for i in range(min_links):
        for node in nodes:
            if len(g.get(node)) < min_links:
                here = g.locations[node]

                def distance_to_node(n):
                    if n is node or g.get(node, n): return infinity
                    return distance(g.locations[n], here)

                neighbor = argmin(nodes, distance_to_node)
                d = distance(g.locations[neighbor], here) * curvature()
                g.connect(node, neighbor, int(d))
    return g


romania = UndirectedGraph(Dict(
    A=Dict(Z=75, S=140, T=118),
    B=Dict(U=85, P=101, G=90, F=211),
    C=Dict(D=120, R=146, P=138),
    D=Dict(M=75),
    E=Dict(H=86),
    F=Dict(S=99),
    H=Dict(U=98),
    I=Dict(V=92, N=87),
    L=Dict(T=111, M=70),
    O=Dict(Z=71, S=151),
    P=Dict(R=97),
    R=Dict(S=80),
    U=Dict(V=142)))
romania.locations = Dict(
    A=(91, 492), B=(400, 327), C=(253, 288), D=(165, 299),
    E=(562, 293), F=(305, 449), G=(375, 270), H=(534, 350),
    I=(473, 506), L=(165, 379), M=(168, 339), N=(406, 537),
    O=(131, 571), P=(320, 368), R=(233, 410), S=(207, 457),
    T=(94, 410), U=(456, 350), V=(509, 444), Z=(108, 531))

australia = UndirectedGraph(Dict(
    T=Dict(),
    SA=Dict(WA=1, NT=1, Q=1, NSW=1, V=1),
    NT=Dict(WA=1, Q=1),
    NSW=Dict(Q=1, V=1)))
australia.locations = Dict(WA=(120, 24), NT=(135, 20), SA=(135, 30),
                           Q=(145, 20), NSW=(145, 32), T=(145, 42), V=(145, 37))






"""
Mapa grande de España para usar con UndirectedGraph (estilo AIMA).

- Península: 47 provincias. Peso = distancia en línea recta (km, fórmula de
  haversine, R=6371 km) entre las capitales de provincias colindantes.
- Canarias: las 7 islas; Gran Canaria y Tenerife detalladas por municipios
  (distancia entre núcleos urbanos principales).
- Enlaces marítimos: distancia en línea recta (km) entre los puertos de las
  rutas de ferry reales (la ruta real puede ser algo mayor).
- Cada arista se declara una sola vez; UndirectedGraph la simetriza.
- Las distancias por carretera serían entre un 15 y un 30 % superiores.
"""

spain = UndirectedGraph(Dict(
    # ---------------- GALICIA ----------------
    COR=Dict(LUG=79.6, PON=105.3),
    LUG=Dict(PON=109.9, OUR=79.3, AST=143.7, LEO=168.6),
    OUR=Dict(PON=65.0, LEO=190.6, ZAM=198.3),
    PON=Dict(),

    # ---------------- NORTE ----------------
    AST=Dict(LEO=87.9, CANT=165.1),
    CANT=Dict(LEO=172.1, PAL=171.9, BUR=124.7, BIZ=74.1),
    BIZ=Dict(BUR=119.6, ALA=51.0, GIP=77.4),
    ALA=Dict(GIP=76.8, NAV=83.7, RIO=46.5, BUR=100.8),
    GIP=Dict(NAV=62.5),
    NAV=Dict(RIO=76.1, ZGZ=143.6, HSC=126.3),
    RIO=Dict(ZGZ=157.1, SOR=77.8, BUR=103.6),

    # ---------------- CASTILLA Y LEÓN ----------------
    LEO=Dict(PAL=107.6, VLL=126.1, ZAM=122.7),
    PAL=Dict(BUR=78.0, VLL=42.9),
    BUR=Dict(VLL=114.6, SEG=159.5, SOR=120.5),
    ZAM=Dict(VLL=86.5, SAL=59.7),
    VLL=Dict(SEG=94.2, AVI=110.8, SAL=109.1),
    SOR=Dict(SEG=164.8, GDL=138.7, ZGZ=131.4),
    SEG=Dict(AVI=57.8, MAD=67.7, GDL=86.5),
    AVI=Dict(SAL=89.7, MAD=86.8, TOL=104.3, CAC=194.8),
    SAL=Dict(CAC=176.8),

    # ---------------- ARAGÓN Y CATALUÑA ----------------
    HSC=Dict(ZGZ=67.2, LLE=102.9),
    ZGZ=Dict(GDL=221.6, TRL=146.1, TGN=187.5, LLE=125.5),
    TRL=Dict(GDL=177.1, CUE=92.7, VLC=115.6, CAS=98.2, TGN=215.9),
    LLE=Dict(TGN=76.1, BCN=131.5, GIR=186.9),
    GIR=Dict(BCN=85.3),
    BCN=Dict(TGN=82.8),
    TGN=Dict(CAS=166.9),

    # ---------------- COMUNIDAD VALENCIANA Y MURCIA ----------------
    CAS=Dict(VLC=63.8),
    VLC=Dict(CUE=164.7, ALB=138.2, ALC=125.4),
    ALC=Dict(ALB=139.7, MUR=69.0),

    # ---------------- CENTRO ----------------
    MAD=Dict(TOL=67.5, CUE=138.4, GDL=51.4),
    GDL=Dict(CUE=107.4),
    TOL=Dict(CUE=162.7, CRE=97.8, BAD=275.6, CAC=205.3),
    CUE=Dict(CRE=195.3, ALB=122.0),
    CRE=Dict(ALB=179.0, JAE=134.8, CBA=142.8, BAD=263.3),
    ALB=Dict(JAE=215.5, GRA=253.0, MUR=128.2),

    # ---------------- EXTREMADURA Y ANDALUCÍA ----------------
    CAC=Dict(BAD=84.0),
    BAD=Dict(HLV=179.9, SEV=186.8, CBA=220.5),
    HLV=Dict(SEV=86.1),
    SEV=Dict(CBA=119.7, MLG=157.3, CDZ=99.6),
    CBA=Dict(JAE=88.2, GRA=130.7, MLG=133.6),
    JAE=Dict(GRA=69.0),
    GRA=Dict(MUR=235.6, ALM=107.8, MLG=89.0),
    ALM=Dict(MUR=174.5, MEL=176.3),
    MLG=Dict(CDZ=168.0),
    CDZ=Dict(CEU=28.8),

    # ---------------- BALEARES (por mar) ----------------
    MLL=Dict(MEN=63.2, IBZ=125.3, BCN=202.4),
    IBZ=Dict(FOR=19.9, ALC=115.4),
    MEN=Dict(),
    FOR=Dict(),
    CEU=Dict(),
    MEL=Dict(),

    # ---------------- CANARIAS: islas ----------------
    LAN=Dict(FUE=14.4),
    FUE=Dict(LPGC=158.3),
    LP=Dict(GOM=91.7),
    GOM=Dict(HIE=85.2),
    HIE=Dict(),

    # ---------------- CANARIAS: GRAN CANARIA (municipios) ----------------
    # LPGC=Las Palmas de GC, ARU=Arucas, TRR=Teror, SBR=Santa Brígida,
    # TEL=Telde, VSQ=Valsequillo, VSM=Vega de San Mateo, ING=Ingenio,
    # AGU=Agüimes, SLU=Santa Lucía, SBT=San Bartolomé de Tirajana,
    # TEJ=Tejeda, MOG=Mogán, ALD=La Aldea, AGA=Agaete, GAL=Gáldar,
    # SMG=Santa María de Guía, MOY=Moya
    LPGC=Dict(ARU=8.5, TRR=13.0, SBR=11.3, TEL=14.7, SCT=88.6, FUE=158.3, LAN=203.2, CDZ=1266.0),
    ARU=Dict(TRR=6.9, MOY=6.2),
    TRR=Dict(SBR=7.0, VSM=5.8),
    SBR=Dict(TEL=7.7, VSQ=3.9, VSM=4.5),
    TEL=Dict(VSQ=7.4, ING=8.1),
    VSQ=Dict(VSM=3.5, TEJ=12.0, SLU=10.4, ING=10.3),
    VSM=Dict(TEJ=9.2),
    ING=Dict(AGU=2.0, SLU=10.4),
    AGU=Dict(SBT=12.6, SLU=9.3),
    SBT=Dict(MOG=15.6, TEJ=9.2, SLU=3.4),
    TEJ=Dict(ALD=16.5, MOG=16.3, SLU=11.9),
    MOG=Dict(ALD=13.1),
    ALD=Dict(AGA=15.0),
    AGA=Dict(GAL=7.1, SCT=66.9),
    GAL=Dict(SMG=2.5),
    SMG=Dict(MOY=4.8),
    MOY=Dict(),
    SLU=Dict(),

    # ---------------- CANARIAS: TENERIFE (municipios) ----------------
    # SCT=Santa Cruz, LAG=La Laguna, ROS=El Rosario, CDL=Candelaria,
    # GUM=Güímar, ARI=Arico, GRN=Granadilla, ARO=Arona, ADE=Adeje,
    # GDI=Guía de Isora, STE=Santiago del Teide, ICO=Icod, ORO=La Orotava,
    # REA=Los Realejos, PCR=Puerto de la Cruz, SUR=Santa Úrsula, TAC=Tacoronte
    SCT=Dict(LAG=6.6, ROS=6.5, LP=150.5),
    LAG=Dict(ROS=5.8, TAC=9.4),
    ROS=Dict(CDL=10.8),
    CDL=Dict(GUM=5.8),
    GUM=Dict(ARI=16.7),
    ARI=Dict(GRN=11.1),
    GRN=Dict(ARO=10.5),
    ARO=Dict(ADE=5.1, GOM=38.3),
    ADE=Dict(GDI=11.2, STE=20.8),
    GDI=Dict(STE=9.6),
    STE=Dict(ICO=12.3),
    ICO=Dict(ORO=19.1),
    ORO=Dict(REA=6.7, PCR=3.4, SUR=5.2),
    REA=Dict(PCR=6.6),
    SUR=Dict(TAC=9.6),
    TAC=Dict(),
    PCR=Dict()))

spain.locations = Dict(
    COR=(-8.4115, 43.3623), LUG=(-7.5558, 43.0121), OUR=(-7.8639, 42.3358), PON=(-8.6444, 42.431),
    AST=(-5.8494, 43.3614), CANT=(-3.81, 43.4623), BIZ=(-2.935, 43.263), ALA=(-2.6716, 42.8467),
    GIP=(-1.9812, 43.3183), NAV=(-1.6458, 42.8125), RIO=(-2.4449, 42.4627), LEO=(-5.5671, 42.5987),
    PAL=(-4.5288, 42.0096), BUR=(-3.6969, 42.3439), ZAM=(-5.7446, 41.5033), VLL=(-4.7245, 41.6523),
    SOR=(-2.4649, 41.7636), SEG=(-4.1088, 40.9429), AVI=(-4.6818, 40.6564), SAL=(-5.6635, 40.9701),
    HSC=(-0.4087, 42.1362), ZGZ=(-0.8891, 41.6488), TRL=(-1.1065, 40.3456), LLE=(0.62, 41.6176),
    GIR=(2.8214, 41.9794), BCN=(2.1686, 41.3874), TGN=(1.2445, 41.1189), CAS=(-0.0513, 39.9864),
    VLC=(-0.3763, 39.4699), ALC=(-0.481, 38.3452), MUR=(-1.1307, 37.9922), MAD=(-3.7038, 40.4168),
    GDL=(-3.1667, 40.6333), TOL=(-4.0273, 39.8628), CUE=(-2.1374, 40.0704), CRE=(-3.9291, 38.9863),
    ALB=(-1.8585, 38.9943), CAC=(-6.3724, 39.4753), BAD=(-6.9707, 38.8794), HLV=(-6.9447, 37.2614),
    SEV=(-5.9845, 37.3891), CBA=(-4.7794, 37.8882), JAE=(-3.7849, 37.7796), GRA=(-3.5986, 37.1773),
    ALM=(-2.4637, 36.834), MLG=(-4.4214, 36.7213), CDZ=(-6.2886, 36.5271), MLL=(2.6502, 39.5696),
    MEN=(4.2658, 39.8885), IBZ=(1.4206, 38.9067), FOR=(1.416, 38.733), CEU=(-5.3213, 35.8894),
    MEL=(-2.9381, 35.2923), LAN=(-13.5477, 28.963), FUE=(-13.8627, 28.5004), LP=(-17.7642, 28.6835),
    GOM=(-17.1133, 28.0916), HIE=(-17.9158, 27.8063), LPGC=(-15.4363, 28.1235), ARU=(-15.5233, 28.119),
    TRR=(-15.5481, 28.0605), SBR=(-15.4846, 28.0309), TEL=(-15.4192, 27.9924), VSQ=(-15.4947, 27.997),
    VSM=(-15.5256, 28.0127), ING=(-15.435, 27.9209), AGU=(-15.4458, 27.9054), SLU=(-15.5399, 27.9122),
    SBT=(-15.572, 27.9229), TEJ=(-15.6168, 27.9951), MOG=(-15.7243, 27.8838), ALD=(-15.7849, 27.9885),
    AGA=(-15.7, 28.1004), GAL=(-15.6508, 28.1472), SMG=(-15.6277, 28.1385), MOY=(-15.5867, 28.1154),
    SCT=(-16.2518, 28.4636), LAG=(-16.3141, 28.4874), ROS=(-16.31, 28.435), CDL=(-16.3714, 28.3544),
    GUM=(-16.412, 28.3167), ARI=(-16.4881, 28.1822), GRN=(-16.5764, 28.1196), ARO=(-16.6811, 28.099),
    ADE=(-16.726, 28.1227), GDI=(-16.7813, 28.2113), STE=(-16.8112, 28.2937), ICO=(-16.7167, 28.3667),
    ORO=(-16.5236, 28.3908), REA=(-16.587, 28.367), PCR=(-16.5463, 28.4139), SUR=(-16.4896, 28.4272),
    TAC=(-16.4096, 28.4767))






class GPSProblem(Problem):
    """The problem of searching in a graph from one node to another."""

    def __init__(self, initial, goal, graph):
        Problem.__init__(self, initial, goal)
        self.graph = graph

    def successor(self, A):
        """Return a list of (action, result) pairs."""
        return [(B, B) for B in list(self.graph.get(A).keys())]

    def path_cost(self, cost_so_far, A, action, B):
        return cost_so_far + (self.graph.get(A, B) or infinity)

    def h(self, node):
        """h function is straight-line distance from a node's state to goal."""
        locs = getattr(self.graph, 'locations', None)
        if locs:
            return int(distance(locs[node.state], locs[self.goal]))
        else:
            return infinity
