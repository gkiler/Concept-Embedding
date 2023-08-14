import logging
import os
from typing import Dict
from tqdm import tqdm
from umlsparser.model.Concept import Concept
from umlsparser.model.SemanticType import SemanticType

UMLS_sources_by_language = {
    'ENG': ['AIR', 'ALT', 'AOD', 'AOT', 'ATC', 'BI', 'CCC', 'CCPSS', 
            'CCS', 'CCSR_ICD10CM', 'CCSR_ICD10PCS', 'CDCREC', 'CDT', 
            'CHV', 'COSTAR', 'CPM', 'CPT', 'CSP', 'CST', 'CVX', 'DDB', 
            'DRUGBANK', 'DSM-5', 'DXP', 'FMA', 'GO', 'GS', 'HCDT', 
            'HCPCS', 'HCPT', 'HGNC', 'HL7V2.5', 'HL7V3.0', 'HPO', 
            'ICD10', 'ICD10AE', 'ICD10AM', 'ICD10AMAE', 'ICD10CM', 
            'ICD10PCS', 'ICD9CM', 'ICF', 'ICF-CY', 'ICNP', 'ICPC', 
            'ICPC2EENG', 'ICPC2ICD10ENG', 'ICPC2P', 'JABL', 'LCH', 
            'LCH_NW', 'LNC', 'MCM', 'MDR', 'MED-RT', 'MEDCIN', 
            'MEDLINEPLUS', 'MMSL', 'MMX', 'MSH', 'MTH', 'MTHCMSFRF', 
            'MTHICD9', 'MTHICPC2EAE', 'MTHICPC2ICD10AE', 'MTHMST', 
            'MTHSPL', 'MVX', 'NANDA-I', 'NCBI', 'NCI', 'NDDF', 'NEU', 
            'NIC', 'NOC', 'NUCCHCPT', 'OMIM', 'OMS', 'ORPHANET', 
            'PCDS', 'PDQ', 'PNDS', 'PPAC', 'PSY', 'QMR', 'RAM', 
            'RCD', 'RCDAE', 'RCDSA', 'RCDSY', 'RXNORM', 'SNM', 
            'SNMI', 'SNOMEDCT_US', 'SNOMEDCT_VET', 'SOP', 'SPN', 
            'SRC', 'ULT', 'UMD', 'USP', 'USPMG', 'UWDA', 'VANDF', 
            'WHO']
}


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UMLSParser:

    def __init__(self, path: str, language_filter: list = ['ENG']):
        """
        :param path: Basepath to UMLS data files
        :param languages: List of languages with three-letter style language codes (if empty, no filtering will be applied)
        """
        logger.info("Initialising UMLSParser for basepath {}".format(path))
        if language_filter:
            logger.info("Language filtering for {}".format(",".join(language_filter)))
        else:
            logger.info("No language filtering applied.")
        self.paths = {
            'MRCONSO': os.path.join(path, 'META', 'MRCONSO.RRF'),
            'MRDEF': os.path.join(path, 'META', 'MRDEF.RRF'),
            'MRSTY': os.path.join(path, 'META', 'MRSTY.RRF'),
            'MRREL': os.path.join(path, "META", 'MRREL.RRF'),
            'SRDEF': os.path.join(path, 'NET', 'SRDEF'),
        }
        self.language_filter = language_filter
        self.concepts = {}
        self.semantic_types = {}
        self.__parse_mrrel__()
        self.__parse_mrconso__()
        self.__parse_mrdef__()
        self.__parse_mrsty__()
        
        # self.__parse_srdef__()

    def __get_or_add_concept__(self, cui: str) -> Concept:
        concept = self.concepts.get(cui, Concept(cui))
        self.concepts[cui] = concept
        return concept

    def __get_or_add_semantic_type__(self, tui: str) -> SemanticType:
        semantic_type = self.semantic_types.get(tui, SemanticType(tui))
        self.semantic_types[tui] = semantic_type
        return semantic_type

    def __parse_mrconso__(self):
        
        for line in tqdm(open(self.paths['MRCONSO'], encoding='utf-8'), desc='Parsing UMLS concepts (MRCONSO.RRF)'):
            line = line.split('|')
            data = {
                'CUI': line[0],
                'LAT': line[1],  # language of term
                'TS': line[2],  # term status
                'LUI': line[3],
                'STT': line[4],
                'SUI': line[5],
                'ISPREF': line[6],
                'AUI': line[7],
                'SAUI': line[8],
                'SCUI': line[9],
                'SDUI': line[10],
                'SAB': line[11],  # source abbreviation
                'TTY': line[12],
                'CODE': line[13],  # Unique Identifier or code for string in source
                'STR': line[14],  # description string
                'SRL': line[15],
                'SUPPRESS': line[16],
                'CVF': line[17]
            }
            
            if len(self.language_filter) != 0 and data.get('LAT') not in self.language_filter:
                continue
            concept = self.__get_or_add_concept__(data.get('CUI'))
            concept.__add_mrconso_data__(data)
        logger.info('Found {} unique CUIs'.format(len(self.concepts.keys())))

    def __parse_mrdef__(self):
        source_filter = []
        for language in self.language_filter:
            for source in UMLS_sources_by_language.get(language):
                source_filter.append(source)

        for line in tqdm(open(self.paths['MRDEF'], encoding='utf-8'), desc='Parsing UMLS definitions (MRDEF.RRF)'):
            line = line.split('|')
            data = {
                'CUI': line[0],
                'AUI': line[1],
                'ATUI': line[2],
                'SATUI': line[3],
                'SAB': line[4],  # source
                'DEF': line[5],  # definition
                'SUPPRESS': line[6],
                'CVF': line[7]
            }
            if len(self.language_filter) != 0 and data.get('SAB') not in source_filter:
                continue
            
            concept = self.__get_or_add_concept__(data.get('CUI'))
            concept.__add_mrdef_data__(data)

    def __parse_mrsty__(self):
        for line in tqdm(open(self.paths['MRSTY'], encoding='utf-8'), desc='Parsing UMLS semantic types (MRSTY.RRF)'):
            line = line.split('|')
            data = {
                'CUI': line[0],
                'TUI': line[1],
                'STN': line[2],  # empty in MRSTY.RRF ?
                'STY': line[3],  # empty in MRSTY.RRF ?
                'ATUI': line[4],  # empty in MRSTY.RRF ?
                'CVF': line[5]  # empty in MRSTY.RRF ?
            }
            concept = self.__get_or_add_concept__(data.get('CUI'))
            concept.__add_mrsty_data__(data)

    def __parse_srdef__(self):
        for line in tqdm(open(self.paths['SRDEF'], encoding='utf-8'), desc='Parsing UMLS semantic net definitions (SRDEF)'):
            line = line.split('|')
            data = {
                'RT': line[0],  # Semantic Type (STY) or Relation (RL)
                'UI': line[1],  # Identifier
                'STY_RL': line[2],  # Name of STY / RL
                'STN_RTN': line[3],  # Tree Number of STY / RL
                'DEF': line[4],  # Definition of STY / RL
                'EX': line[5],  # Examples of Metathesaurus concepts
                'UN': line[6],  # Usage note for STY assignment
                'NH': line[7],  # STY and descendants allow the non-human flag
                'ABR': line[8],  # Abbreviation of STY / RL
                'RIN': line[9]  # Inverse of the RL
            }
            semantic_type = self.__get_or_add_semantic_type__(data['UI'])
            semantic_type.__add_srdef_data__(data)
        logger.info('Found {} unique TUIs'.format(len(self.semantic_types.keys())))

####################################################################################################
# testing stuff
    def __parse_mrrel__(self):
        cnt=0
        rels = set()
        wanted_rels = ["RN","RB","CHD","PAR"]
        for line in tqdm(open(self.paths['MRREL'], encoding='utf-8'), desc='Parsing UMLS relations (MRREL.RRF)'):
            line = line.split('|')
            data = {
                'CUI1': line[0],
                'AUI1': line[1],
                'STYPE1': line[2],
                'REL': line[3],
                'CUI2': line[4],
                'AUI2': line[5],
                'STYPE2': line[6],
                'RELA': line[7],
                'RUI': line[8],
                'SRUI': line[9],
                'SAB': line[10],
                'SL': line[11],
                'RG': line[12],
                'DIR': line[13],
                'SUPPRESS': line[14],
            }
            if (len(self.language_filter) != 0 and data.get('SAB') not in UMLS_sources_by_language['ENG']):
                continue
            
            if data.get('REL') in wanted_rels:
                cnt+=1
                concept = self.__get_or_add_concept__(data.get('CUI1'))
                concept.__add_mrrel_data__(data)
            #TODO add relations markers. link cui1 to cui2 for each concept
            # concept = self.__get_or_add_concept__(data.get('CUI'))
            # concept.__add_mrconso_data__(data)
        logger.info('Found {} unique Relations'.format(cnt))


#######################################################################################################################################
    def get_concepts(self) -> Dict[str, Concept]:
        """
        :return: A dictionary of all detected UMLS concepts with CUI being the key.
        """
        return self.concepts

    def get_semantic_types(self) -> Dict[str, SemanticType]:
        """
        :return: A dictionary of all detected UMLS semantic types with TUI being the key.
        """
        return self.semantic_types

    def get_languages(self):
        return self.language_filter
