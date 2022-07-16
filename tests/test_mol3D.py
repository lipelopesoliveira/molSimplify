import pytest
import numpy as np
from molSimplify.Classes.mol3D import mol3D
from molSimplify.Classes.atom3D import atom3D
from pkg_resources import resource_filename, Requirement


def test_adding_and_deleting_atoms():
    mol = mol3D()
    mol.addAtom(atom3D(Sym='Fe'))

    assert mol.natoms == 1
    assert mol.findMetal() == [0]

    mol.addAtom(atom3D(Sym='Cu'))

    assert mol.natoms == 2
    assert mol.findMetal() == [0, 1]

    mol.deleteatom(0)

    assert mol.natoms == 1
    assert mol.findMetal() == [0]


def test_finding_and_counting_methods():
    mol = mol3D()
    mol.addAtom(atom3D(Sym='Fe'))
    for _ in range(6):
        mol.addAtom(atom3D(Sym='C'))
        mol.addAtom(atom3D(Sym='O'))

    # Test find_atom
    assert mol.find_atom(sym='O') == [2, 4, 6, 8, 10, 12]
    # Test findAtomsbySymbol
    assert mol.findAtomsbySymbol(sym='C') == [1, 3, 5, 7, 9, 11]
    # Test getAtomwithSyms (allows for multiple symbols)
    ref_indices = [0, 2, 4, 6, 8, 10, 12]
    assert (mol.getAtomwithSyms(syms=['Fe', 'O'])
            == [mol.getAtom(i) for i in ref_indices])
    # optional argument allows to return just the indices:
    assert (mol.getAtomwithSyms(syms=['Fe', 'O'], return_index=True)
            == ref_indices)
    # Test mols_symbols
    mol.mols_symbols()
    assert mol.symbols_dict == {'Fe': 1, 'C': 6, 'O': 6}
    # Test count_nonH_atoms
    assert mol.count_nonH_atoms() == 13
    # Test count_atoms (exclude O)
    assert mol.count_atoms(exclude=['H', 'O']) == 7
    # Test count_specific_atoms
    assert mol.count_specific_atoms(atom_types=['C', 'O']) == 12
    # Test count_electrons
    assert mol.count_electrons(charge=2) == 24 + 6*6 + 6*8
    # Test findcloseMetal
    assert mol.findcloseMetal(mol.getAtom(-1)) == 0
    # Test findMetal
    assert mol.findMetal() == [0]
    # Test make_formula (sorted by atomic number)
    assert mol.make_formula(latex=False) == 'Fe1O6C6'
    assert (mol.make_formula(latex=True)
            == r'\textrm{Fe}_{1}\textrm{O}_{6}\textrm{C}_{6}')
    # Test typevect
    np.testing.assert_equal(mol.typevect(), np.array(['Fe'] + ['C', 'O']*6))


def test_add_bond():
    mol = mol3D()
    mol.addAtom(atom3D(Sym='O'))
    mol.addAtom(atom3D(Sym='C'))
    mol.addAtom(atom3D(Sym='H'))
    mol.addAtom(atom3D(Sym='H'))

    # Initialize empty bo_dict and graph
    mol.bo_dict = {}
    mol.graph = np.zeros((4, 4))

    mol.add_bond(0, 1, 2)
    mol.add_bond(1, 2, 1)
    mol.add_bond(1, 3, 1)

    assert mol.bo_dict == {(0, 1): 2, (1, 2): 1, (1, 3): 1}
    np.testing.assert_allclose(mol.graph, [[0, 2, 0, 0],
                                           [2, 0, 1, 1],
                                           [0, 1, 0, 0],
                                           [0, 1, 0, 0]])

    # Assert that bonding an atom to itself fails:
    with pytest.raises(IndexError):
        mol.add_bond(0, 0, 1)

    new_bo_dict = mol.get_bo_dict_from_inds([1, 2, 3])
    assert new_bo_dict == {(0, 1): 1, (0, 2): 1}

    assert mol.get_mol_graph_det(oct=False) == '-154582.1094'
    assert mol.get_mol_graph_det(oct=False, useBOMat=True) == '-154582.1094'


@pytest.mark.skip(reason='Mutating the state of an atom3D can not be detected '
                         ' by the mol3D class')
def test_mutating_atoms():
    mol = mol3D()
    mol.addAtom(atom3D(Sym='Fe'))
    assert mol.findMetal() == [0]

    mol.atoms[0].mutate('C')
    assert mol.findMetal() == []


@pytest.mark.parametrize('name, coordination_number, geometry_str', [
    ('trigonal_planar', 3, 'trigonal planar'),
    ('t_shape', 3, 'T shape'),
    ('trigonal_pyramidal', 3, 'trigonal pyramidal'),
    ('tetrahedral', 4, 'tetrahedral'),
    ('square_planar', 4, 'square planar'),
    ('seesaw', 4, 'seesaw'),
    ('trigonal_bipyramidal', 5, 'trigonal bipyramidal'),
    ('square_pyramidal', 5, 'square pyramidal'),
    # ('pentagonal_planar', 5, 'pentagonal planar'),
    ('octahedral', 6, 'octahedral'),
    # ('pentagonal_pyramidal', 6, 'pentagonal pyramidal'),
    ('trigonal_prismatic', 6, 'trigonal prismatic'),
    # ('pentagonal_bipyramidal', 7, 'pentagonal bipyramidal')
    ])
def test_geometry_functions(name, coordination_number, geometry_str):
    xyz_file = resource_filename(
        Requirement.parse("molSimplify"),
        f"tests/refs/geometry_type/{name}.xyz"
    )
    mol = mol3D()
    mol.readfromxyz(xyz_file)

    geo_report = mol.get_geometry_type(num_coord=coordination_number)

    assert geo_report['geometry'] == geometry_str
    assert geo_report['allconnect'] is False
    assert geo_report['aromatic'] is False
