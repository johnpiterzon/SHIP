"""

 Summary:
    Contains the AIsisUnit, CommentUnit, HeaderUnit and UnknownSection 
    classes.
    The AIsisUnit is an abstract base class for all types of Isis unit read
    in through the ISIS data file. All section types that are built should
    inherit from the AIsisUnit baseclass.

 Author:  
     Duncan Runnacles

 Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""
from __future__ import unicode_literals

import hashlib
import uuid
import random
import copy
# from abc import ABCMeta, abstractmethod

from ship.isis.datunits import ROW_DATA_TYPES as rdt
from ship.data_structures import DATA_TYPES as dt
from ship.isis.headdata import HeadDataItem

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""

    
class AIsisUnit(object): 
    """Abstract base class for all Dat file units.
    
    This class must be inherited by all classes representing an isis
    data file unit (such as River, Junction, Culvert, etc).
    
    Every subclass should override the readUnitData() and getData() methods to 
    ensure they are specific to the setup of the individual units variables.
    If they are not overridden this class will simply take the data and store it
    as read and provide it back in the same state.
    
    All calls from the client to these classes should create the object and then
    call the readUnitData() method with the raw data.
    
    There is an UknownSection class at the bottom of this file that can be used 
    for all parts of the isis dat file that have not had a class defined. It just
    calls the basic read-in read-out methods from this class and understands nothing
    about the structure of the file section it is holding.     
    
    See Also:
        UnknownSection
    """
#     __metaclass__ = ABCMeta
        
    
    def __init__(self, **kwargs):
        """Constructor
        
        Set the defaults for all unit specific variables.
        These should be set by each unit at some point in the setup process.
        E.g. RiverUnit would set type and UNIT_CATEGORY at __init__() while name
        and data_objects are set in the readUnitData() method.
        Both of these are called at or immediately after initialisation.
        """
        
        self._name = 'unknown'                   # Unit label
        self._name_ds = 'unknown'                # Unit downstream label
        
        self._data = None                       
        """This is used for catch-all data storage.
        
        Used in units such as UnknownSection.
        Classes that override the readUnitData() and getData() methods are
        likely to ignore this variable and use row_collection and head_data instead.
        """
        
        self._unit_type = 'Unknown'
        """The type of ISIS unit - e.g. 'River'"""

        self._unit_category = 'Unknown'
        """The ISIS unit category - e.g. for type 'Usbpr' it would be 'Bridge'"""
        
#         self.has_datarows = False      
        """Flag stating whether the unit contains an unknown no. of data rows.
        
        This could be geometry in river or bridge units etc, or other data
        rows like inital conditions or hydrograph values.
        
        If False then the unit only contains head_data. A dictionary containing
        set values that are always present in the file - e.g. Orifice.
        """
        
#         self.no_of_collections = 1                           
        """Total number of row collections held by this file. 
        
        If set to zero it means the same as has_datarows = False. Set to one as 
        default because zero is dealt with by has_datarows and if that is set 
        to True then there must be at least 1 row_collection.
        """

#         self.row_collection = None 
        self.row_data = {} 
        """Collection containing all of the ADataRow objects.
        
        This is the main collection for row data in any unit that contains it.
        In a RiverUnit, for example, this will hold the RowDataObject's 
        containing the CHAINAGE, ELEVATION, etc.
        """
        
#         self.additional_row_collections = None  
        """Flag stating whether the unit contains additional row data.
        
        This is used for units that contain more than one set of unknow length
        data series - e.g. opening data in bridges.
        
        If this is used it should be instanciated as an OrderedDict
        """

        self.head_data = {}
        """Dictionary containing set values that are always present in the file.
        
        In a RiverUnit this includes values like slope and distance. I.e.
        values that appear in set locations, usually at the top of the unit
        data in the .dat file.
        """

        
#         self.ic_labels = []
        
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def name_ds(self):
        return self._name_ds
    
    @name_ds.setter
    def name_ds(self, value):
        self._name_ds = value
        
    @property
    def has_ics(self):
        if not self.icLabels():
            return False
        else:
            return True
    
    @property
#     def has_row_data(self):
    def hasRowData(self):
        if not self.row_data:
            return False
        else:
            return True
    
    @property
    def unit_type(self):
        return self._unit_type

    @property
    def unit_category(self):
        return self._unit_category

    
    def icLabels(self):
        """Returns the initial_conditions values for this object.
        
        This method should be overriden by all classes that contain intial
        conditions.
        
        For example a BridgeUnit type will have two initial conditions labels;
        the upstream and downstream label names.
        
        By default this will return an empty list.
        
        Return:
            list - of intial condition label names.
        """
        return [] 
        
        
#     def getUnitVars(self): 

        
#     # TODO: These are superflous methods. Need removing.
#     def getName( self ): 

        
#     def getUnitType( self ):
#     def unitType(self):


#     def getUnitUNIT_CATEGORY(self):

    
    
#     def getDeepCopy(self):
    def copy(self):
        """Returns a copy of this unit with it's own memory allocation."""
        object_copy = copy.deepcopy(self)
        return object_copy
    
    
#     def getRowDataType(self, key, collection_key='main', copy=False):
    def rowDataType(self, key, rowdata_key='main'):
        """Getter for the data series in the data_object dictionary.

        Depending on the data that the subclass contains this could be 
        anything... a dictionary a string a integer. It is up to the client 
        and the subclass to ensure that this is clear.
        
        Args:
            key (str): The key for the data_object requested.
            collection_key='main' (str): the key for the row_collection to 
                return. Most objects will only contain a single row_collection,
                like the RiverUnit, but some like bridges have opening data and
                orifice data rows as well. See individual AIsisUnit 
                implemenations for more details on what they contain.
        
        Returns:
            DataObject requested by client or False if unit has no rows.
        
        Raises:
            KeyError: If key does not exist. 
        """
        if not self.has_datarows:
            return False
        try:
            return self.row_data[rowdata_key].getDataObject(key)
        except KeyError:
            logger.warning('Key %s does not exist in collection' % (key))
            raise KeyError ('Key %s does not exist in collection' % (key))
    
    
#     def getRowDataTypeAsList(self, key, collection_key='main'):
    def rowDataTypeAsList(self, key, rowdata_key='main'):
        """Returns the row data object as a list.

        This will return the row_collection data object referenced by the key
        provided in list form.

        If you intend to update the values you should use getRowDataObject
        instead as the data provided will be mutable and therefore reflected in
        the values held by the row_collection. If you just want a quick way to
        loop through the values in one of the data objects  and only intend to
        read the data then use this.
        
        Args:
            key (str): the key for the data object requested. It is best to use 
               the class constants (i.e. RiverUnit.CHAINAGE) for this.
        
        Returns:
            List containing the data in the DataObject that the key points
                 to. Returns false if there is no row collection.
        
        Raises:
            KeyError: If key does not exist.
        """
        if not self.has_datarows:
            return False
        try:
            data_col = self.row_data[rowdata_key].getDataObject(key)
            vals = []
            for i in range(0, data_col.record_length):
                vals.append(data_col.getValue(i))
            return vals
        except KeyError:
            logger.warning('Key %s does not exist in collection' % (key))
            raise KeyError ('Key %s does not exist in collection' % (key))
    
    
#     def getRow(self, index):
    def row(self, index, rowdata_key='main'):
        """Get the data vals in a particular row by index.
        
        Args:
            index(int): the index of the row to return.
            
        Return:
            dict - containing the values for the requested row.
        """
        return self.row_data[rowdata_key].row(index)
    
     
#     def getHeadData(self):
#         """Returns the header data from this unit.
#  
#         This includes the details outlined at the top of the unit such as the
#         unit name, labels, global variables, etc.
#         for some units, such as HeaderUnit or Junctions this is all of the 
#         data. Other units, such as the RiverUnit also have RowDataObjects.
#         
#         Note:
#             Must be overriden by all concrete classes.
#          
#         Returns:
#             The header data for this unit or None if it hasn't been initialised.
#         """
#         raise NotImplementedError


    def getData(self): 
        """Getter for the unit data.
  
        Return the file geometry data formatted ready for saving in the style
        of an ISIS .dat file
          
        Note:
            This method should be overriden by the sub class to restore the 
            data to the format required by the dat file.
          
        Returns:
            List of strings - formatted for writing to .dat file.
        """
        raise NotImplementedError
    

    def readUnitData(self, data, file_line, **kwargs):
        """Reads the unit data supplied to the object.
        
        This method is called by the IsisUnitFactory class when constructing the
        Isis  unit based on the data passed in from the dat file.
        The default hook just copies all the data parsed in the buildUnit() 
        method of the factory and aves it to the given unit. This is exactly
        what happens for the UnknownUnit class that just maintains a copy of the
        unit data exactly as it was read in.
        
        Args:
            data (list): raw data for the section as supplied to the class.

        Note:
            When a class inherits from AIsisUnit it should override this method 
            with unit specific load behaviour. This is likely to include: 
            populate unit specific header value dictionary and in some units 
            creating row data object.
        
        See Also: 
            RiverSection for an example of overriding this method with a 
                concrete class. 
              
        """ 
        self.head_data['all'] = data
        
    
#     def deleteDataRow(self, index, rowdata_key=None):
    def deleteRow(self, index, rowdata_key='main'):
        """Removes a data row from the RowDataCollection.
        """
        if index < 0 or index >= self.row_data[rowdata_key].numberOfRows():
            raise IndexError ('Given index is outside bounds of row_data[rowdata_key] data')
        
        self.row_data[rowdata_key].deleteRow(index)
        
    
    # DEBUG
    # TODO
#     def updateDataRow(self, row_vals, index=None, rowdata_key='main'):
    def updateRow(self, row_vals, index=None, rowdata_key='main'):
        """
        """
        if index >= self.row_data[rowdata_key].numberOfRows():
            raise IndexError ('Given index is outside bounds of row_collection data')
        
#         # Check that there won't be a negative change in chainage across row.
#         c = row_vals.get(rdt.CHAINAGE)
#         if check_negative and not c is None:
#             if self._checkChainageIncreaseNotNegative(index, 
#                                         row_vals.get(rdt.CHAINAGE)) == False:
#                 logger.error('Chainage increase is negative')
#                 raise ValueError ('Chainage increase is negative')
        
        # Call the row collection add row method to add the new row.
        if collection_name is None:
            self.row_collection.updateRow(values_dict=row_vals, index=index)
        
        else:
            self.additional_row_collections[collection_name].updateRow(
                                        values_dict=row_vals, index=index)
            
    
#     def addDataRow(self, row_vals, collection_name=None, index=None, 
#                                                 check_negative=True):
    
    def addRow(self, row_vals, rowdata_key='main', index=None):
        """Add a new data row to one of the row data collections.
        
        Provides the basics of a function for adding additional row dat to one
        of the RowDataCollection's held by an AIsisUnit type.
        
        Checks that key required variables: ROW_DATA_TYPES.CHAINAGE amd 
        ROW_DATA_TYPES.ELEVATION are in the kwargs and that inserting chainge in
        the specified location is not negative, unless check_negatie == False.
        
        It then passes the kwargs directly to the RowDataCollection's
        addNewRow function. It is the concrete class implementations 
        respnsobility to ensure that these are the expected values for it's
        row collection and to set any defaults. If they are not as expected by
        the RowDataObjectCollection a ValueError will be raised.
        
        Args:
            row_vals(dict): Named arguments required for adding a row to the 
                collection. These will be as stipulated by the way that a 
                concrete implementation of this class setup the collection.
            rowdata_key='main'(str): the name of the RowDataCollection
                held by this to add the new row to. If None it is the
                self.row_collection. Otherwise it is the name of one of the
                entries in the self.additional_row_collections dictionary.
            index=None(int): the index in the RowDataObjectCollection to insert
                the row into. If None it will be appended to the end.
        """
        # If index is >= record length it gets set to None and is appended
        if index >= self.row_data[rowdata_key].numberOfRows():
            index = None
        
        self.row_data[rowdata_key].addRow(row_vals, index)
        
    
#     def _checkChainageIncreaseNotNegative(self, index, chainageValue, 
#                                                     collection_name=None):
    def checkIncreases(self, data_obj, value, index):
        """Checks that: prev_value < value < next_value.
        
        If the given value is not greater than the previous value and less 
        than the next value it will return False.
        
        If an index greater than the number of rows in the row_data it will
        check that it's greater than previous value and return True if it is.
        
        Note:
            the ARowDataObject class accepts a callback function called
            update_callback which is called whenever an item is added or
            updated. That is how this method is generally used.

        Args:
            data_obj(RowDataObject): containing the values to check against.
            value(float | int): the value to check.
            index=None(int): index to check ajacent values against. If None
                it will assume the index is the last on in the list.
        
        Returns:
            False if not prev_value < value < next_value. Otherwise True.
        """
        details = self._getAdjacentDataObjDetails(data_obj, value, index)
        if details['prev_value']:
            if not value > details['prev_value']:
                raise ValueError('CHAINAGE must be > prev index and < next index.')
        if details['next_value']:
            if not value < details['next_value']:
                raise ValueError('CHAINAGE must be > prev index and < next index.')
    
    
    def _getAdjacentDataObjDetails(self, data_obj, value, index):
        """Safely check the status of adjacent values in an ADataRowObject.
        
        Fetches values for previous and next indexes in the data_obj if they
        exist.
        
        Note value in return 'index' key will be the given index unless it was
        None, in which case it will be the maximum index.
        
        All other values will be set to None if they do not exist.
        
        Args:
            data_obj(RowDataObject): containing the values to check against.
            value(float | int): the value to check.
            index=None(int): index to check ajacent values against. If None
                it will assume the index is the last on in the list.
        
        Return:
            dict - containing previous and next values and indexes, as well as
                the given index checked for None.
        
        """
        prev_value = None
        next_value = None
        prev_index = None
        next_index = None
        if index is None:
            index = data_obj._max

        if index < 0:
            raise ValueError('Index must be > 0')
        if index > 0: 
            prev_index = index - 1
            prev_value = data_obj[prev_index]
        if index < data_obj._max: 
            next_index = index + 1
            next_value = data_obj[next_index]

        retvals = {'index': index,
                   'prev_value': prev_value, 'prev_index': prev_index, 
                   'next_value': next_value, 'next_index': next_index}
        return retvals


    
class UnknownUnit(AIsisUnit):
    """ Catch all section for unknown parts of the .dat file.
    
    This can be used for all sections of the isis dat file that have not had
    a unit class constructed.

    It has no knowledge of the file section that it contains and will store it 
    without altering it's state and return it in exactly the same format that it
    received it.

    This class is designed to be a fall-back class for any parts of the dat file
    for which it is deemed unnecessary to deal with more carefully.

    It has a 'Section' suffix rather that 'Unit' which is the naming convention
    for the other unit objects because it is not necessarily a single unit. It
    could be many different units. 
    
    It is created whenever the DatLoader finds
    parts of the dat file that it doesn't Know how to load (i.e. there is no
    *Unit defined for it. It will then put all the dat file data in one of these
    until it reaches a part of the file that it does recognise.
    """
    FILE_KEY = 'UNKNOWN'
    FILE_KEY2 = None
     
    def __init__ (self): 
        """Constructor.
        """
        AIsisUnit.__init__(self) 
        self._unit_type = 'unknown'
        self._unit_category = 'unknown'
        self._name = 'unknown_' + str(hashlib.md5(str(random.randint(-500, 500)).encode()).hexdigest()) # str(uuid.uuid4())
    

    def getData(self):
        return self.head_data['all']
    

    def readUnitData(self, data):
        self.head_data['all'] = data


class CommentUnit(AIsisUnit):
    """Holds the data in COMMENT sections of the .dat file.
    
    This is very similar to the UnknownSection in that all it does is grab the
    data between the comment tags and save it. It then prints out the same data
    in the same format with the COMMENT tags around it.
    """
    # Class constants
    UNIT_TYPE = 'comment'
    UNIT_CATEGORY = 'meta'
    FILE_KEY = 'COMMENT'
    FILE_KEY2 = None
       

    def __init__(self, text=''):
        """Constructor.
        """
        AIsisUnit.__init__(self) 
        self._unit_type = CommentUnit.UNIT_TYPE
        self._unit_category = CommentUnit.UNIT_CATEGORY
        self._name = 'comment_' + str(hashlib.md5(str(random.randint(-500, 500)).encode()).hexdigest()) # str(uuid.uuid4())
        self.has_datarows = True
        self.data = []
        if not text.strip() == '': self.addCommentText(text)
        
    
    def addCommentText(self, text):
        text = text.split('\n')
        self.no_of_rows = int(len(self.data) + len(text))
        for t in text:
            self.data.append(t.strip())
     
    def readUnitData(self, data, file_line):
        """
        """
        file_line += 1
        line = data[file_line]
        self.no_of_rows = int(data[file_line].strip())
        file_line += 1
        for i in range(file_line, file_line + self.no_of_rows):
            self.data.append(data[file_line].strip())
            file_line += 1

        return file_line -1 
    
    def getData(self):
        """
        """
        output = []
        output.append('{:<10}'.format('COMMENT'))
        output.append('{:>10}'.format(self.no_of_rows))
        for d in self.data:
            output.append(d)
        
        if len(output) > self.no_of_rows + 2:
            output = output[:self.no_of_rows + 2]
        
        return output


class HeaderUnit(AIsisUnit):
    """This class deals with the data file values at the top of the file.
    
    
    These contain the global variables for the model such as water temperature,
    key matrix coefficients and the total number of nodes.
    
    There is only ever one of these units in every dat file - at the very top -
    so it seems convenient to put it in this module.
    """
    # Class constants
    UNIT_TYPE = 'header'
    UNIT_CATEGORY = 'meta'
    FILE_KEY = 'HEADER'
    FILE_KEY2 = None
    

    def __init__(self):
        """Constructor.
        """
        AIsisUnit.__init__(self)
#         self._unit_type = 'header' 
#         self._unit_category = 'meta'
        self._unit_type = HeaderUnit.UNIT_TYPE
        self._unit_category = HeaderUnit.UNIT_CATEGORY
        self._name = 'header'
        self.has_datarows = False
            
    
    def readUnitData(self, unit_data, file_line): 
        """Reads the given data into the object.
        
        Args:
            unit_data (list): The raw file data to be processed.
        """
        self.head_data = {
            'name': HeadDataItem(unit_data[0].strip(), '', 0, 0, dtype=dt.STRING),
            'revision': HeadDataItem(unit_data[1].strip(), '{:>10}', 1, 0, dtype=dt.STRING),
            'node_count': HeadDataItem(unit_data[2][:10].strip(), '{:>10}', 2, 0, dtype=dt.INT),
            'fr_lower': HeadDataItem(unit_data[2][10:20].strip(), '{:>10}', 2, 1, dtype=dt.FLOAT, dps=3),
            'fr_upper': HeadDataItem(unit_data[2][20:30].strip(), '{:>10}', 2, 2, dtype=dt.FLOAT, dps=3),
            'min_depth': HeadDataItem(unit_data[2][30:40].strip(), '{:>10}', 2, 3, dtype=dt.FLOAT, dps=3),
            'direct_method': HeadDataItem(unit_data[2][40:50].strip(), '{:>10}', 2, 4, dtype=dt.FLOAT, dps=3),
            'unknown': HeadDataItem(unit_data[2][50:60].strip(), '{:>10}', 2, 5, dtype=dt.STRING), 
            'water_temp': HeadDataItem(unit_data[3][:10].strip(), '{:>10}', 3, 0, dtype=dt.FLOAT, dps=3),
            'flow': HeadDataItem(unit_data[3][10:20].strip(), '{:>10}', 3, 1, dtype=dt.FLOAT, dps=3),
            'head': HeadDataItem(unit_data[3][20:30].strip(), '{:>10}', 3, 2, dtype=dt.FLOAT, dps=3),
            'math_damp': HeadDataItem(unit_data[3][30:40].strip(), '{:>10}', 3, 3, dtype=dt.FLOAT, dps=3),
            'pivot': HeadDataItem(unit_data[3][40:50].strip(), '{:>10}', 3, 4, dtype=dt.FLOAT, dps=3),
            'relax': HeadDataItem(unit_data[3][50:60].strip(), '{:>10}', 3, 5, dtype=dt.FLOAT, dps=3),
            'dummy': HeadDataItem(unit_data[3][60:70].strip(), '{:>10}', 3, 6, dtype=dt.FLOAT, dps=3), 
            'roughness': HeadDataItem(unit_data[5].strip(), '{:>10}', 5, 0, dtype=dt.STRING), 
        }
        
        return file_line + 7
        
        
    def getData(self):
        """ Getter for the formatted data to write back to the .dat file.
        
        Returns:
            List - data formatted for writing to the new dat file.
        """
        out_data = []
        out = []
        key_order = ['name', 'revision', 'node_count', 'fr_lower', 'fr_upper', 'min_depth',
                     'direct_method', 'unknown', 'water_temp', 'flow', 'head',
                     'math_damp', 'pivot', 'relax', 'dummy']
#         print ('REFH getData')
        for k in key_order:
#             print(k)
            out.append(self.head_data[k].format(True))
        out = ''.join(out).split('\n')
        
        out.append('RAD FILE')
        out.append(self.head_data['roughness'].format())
        out.append('END GENERAL')
                        
        return out
        