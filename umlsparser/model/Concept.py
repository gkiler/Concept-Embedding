import collections
from dataclasses import dataclass
from typing import Set, Tuple, Dict


@dataclass(init=False, repr=True, eq=True)
class Concept:
    __cui: str
    __tui: str
    __preferred_names: Dict[str, Set[str]]
    __all_names: Dict[str, Set[str]]
    __definitions: Set[Tuple[str, str]]
    __auis: Set[Tuple[str,str]]
    __source_ids: Dict[str, Set[str]]
    __rels: Set[Tuple[str, str]] #(cui,relation)

    def __init__(self, cui: str):
        self.__cui = cui
        self.__tui = None
        self.__auis = set()
        self.__preferred_names = collections.defaultdict(set)
        self.__all_names = collections.defaultdict(set)
        self.__definitions = set()
        self.__rels = set()
        self.__source_ids = collections.defaultdict(set)

    def __add_mrrel_data__(self, data: dict):
        self.__rels.add((data.get('CUI2'),data.get("REL")))

    def __add_mrconso_data__(self, data: dict):
        """
        Adds data to a concept, mostly used during the parsing of an MRCONSO.RRF file.
        :param data: certain fields out of an MRCONSO.RRF file (lat, str)
        :return:
        """
        self.__all_names[data['LAT']].add(data['STR'])
        if data['TS'] == 'P':
            self.__preferred_names[data['LAT']].add(data['STR'])
        if data['SAB'] != '' and data['CODE'] != '':
            self.__source_ids[data['SAB']].add(data['CODE'])

    def __add_mrdef_data__(self, data: dict):
        self.__definitions.add((data.get('DEF'), data.get('SAB')))
        self.__auis.add((data.get("AUI"), data.get("SAB")))

    def __add_mrsty_data__(self, data: dict):
        self.__tui = data.get('TUI')
    
    
        

    def get_preferred_names_for_language(self, lang: str) -> list:
        """
        Returns a set of every concept name that was marked as preferred in MRCONSO.RRF.
       :param lang: Language
       :return: Set of names
       """
        return list(self.__preferred_names.get(lang, []))

    def get_names_for_language(self, lang: str) -> list:
        """
        Returns a set of every concept name that was marked as preferred in MRCONSO.RRF.
       :param lang: Language
       :return: Set of names
       """
        return list(self.__all_names.get(lang, []))

    def get_definitions(self) -> Set[Tuple[str, str]]:
        """
        Returns all found definitions for this concept.
        :return: Set of tuples (definition, source)
        """
        return self.__definitions

    def get_relations(self) -> Set[Tuple[str,str]]:
        return self.__rels
    
    def get_cui(self) -> str:
        """
        :return: CUI
        """
        return self.__cui
    
    def get_auis(self):
        return self.__auis

    def get_tui(self) -> str:
        """
        :return: Semantic Type Identifier
        """
        return self.__tui

    def get_source_ids(self) -> Dict[str, Set[str]]:
        """
        This returns a list of all found codes. Be aware that the codes are determined after the language filter!
        :return: Dict of all unique ids for all sources
        """
        return self.__source_ids

    def __hash__(self):
        return hash(self.__cui)