# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
# Modified new DB: 28-Jun-2109
import xlrd
import csv
# Huong add this line to use for python 3
from xlrd.timemachine import xrange
class Excel():
    def __init__(self, excelfilepath, sheetname=None):
        self.sheetname = sheetname
        self.excelfilepath = excelfilepath

    def openwb(self):
        self._book = xlrd.open_workbook(self.excelfilepath, on_demand = True)        
        return self._book
    
    def openws(self, wbobj = None):
        if wbobj is None:
            wbobj = self.openwb()        
        
        if str(self.sheetname).isdigit():
            self._worksheet = wbobj.sheet_by_index(self.sheetname)            
        else:
            self._worksheet = wbobj.sheet_by_name(self.sheetname)
        return self._worksheet
    
    def releasewb(self, wbobj = None):        
        wbobj.release_resources()
        del wbobj
    
    def getSheetNames(self, wbobj = None):
        result = wbobj.sheet_names()
        result = [str(x) for x in result]
        return result
    
    def isSheetNameExist(self, wbobj = None):
        result = False
        sheetnamelist = self.getSheetNames(wbobj)
        if self.sheetname in sheetnamelist:
            result = True
        return result
    
    def GetCellValue(self, row, col, wsobj):
        result = wsobj.cell_value(rowx=row, colx=col)                
        return result
    
    def GetHeaderColumnName(self, wsobj):
        headerlist = [str(wsobj.cell_value(0, i)) for i in xrange(wsobj.ncols)]
        return headerlist

    def GetHeaderColumnIndex(self, headercolname, wsobj):
        index = -1
        headerlist = self.GetHeaderColumnName(wsobj)
        if headercolname in headerlist:
            index = headerlist.index(headercolname)
        return index

    def GetCellValueByColumnName(self, row, colheadername, wsobj):
        cellvalue = ""
        colheaderindex = self.GetHeaderColumnIndex(colheadername, wsobj)
        if colheaderindex >= 0:
            cellvalue = self.GetCellValue(row, colheaderindex, wsobj)
        return cellvalue
    
    def GetColumnValues(self, headercolname, wsobj):
        columnvalues = []
        indx = self.GetHeaderColumnIndex(headercolname, wsobj)
        columnvalues = [wsobj.cell_value(i, indx) for i in xrange(1, wsobj.nrows)]
        return columnvalues

    def GetRowValues(self, row, wsobj):
        rowvalues = []
        rowvalues = [wsobj.cell_value(row, i) for i in xrange(wsobj.ncols)]
        return rowvalues

    def GetCellIndexByValue(self, value, operator="in", wsobj=None):
        cellindex = []
        for x in xrange(wsobj.nrows):
            rowvalues = self.GetRowValues(x, wsobj)            
            rowvalues = [str(u) for u in rowvalues]
            
            tmp_flag = []
            if operator == "in":
                tmp_flag = [t for t in rowvalues if value in t]
            elif operator == "=":
                tmp_flag = [t for t in rowvalues if value == t]
            
            if len(tmp_flag) > 0:
                col = rowvalues.index("".join(tmp_flag))
                cellindex = [x,col]
                break
        return cellindex

    def GetTotalRows(self, wsobj):
        totalrows = 0
        totalrows = wsobj.nrows
        return totalrows

    def GetTotalCols(self, wsobj):
        totalcols = 0
        totalcols = wsobj.ncols
        return totalcols

    def GetRowIndexByValue(self, columnname, searchvalue, wsobj):
        # This action is used to get row index of given column based on search value
        row = -1
        colindx = self.GetHeaderColumnIndex(columnname, wsobj)
        for i in xrange(1, wsobj.nrows):
            cellvalue = self.GetCellValue(i, colindx, wsobj)
            if searchvalue in cellvalue:
                row = i
                break
        return row

    def GetRowIndexesByFilter(self, columnname, filtervalue, operater="=", wsobj=None):
        # this action is used to get list row index based on filter column value
        rows = []        
        colindx = self.GetHeaderColumnIndex(columnname, wsobj)        
        for i in xrange(1, wsobj.nrows):
            cellvalue = self.GetCellValue(i, colindx, wsobj)
            expr = False
            if operater == "=":
                expr = filtervalue == cellvalue
            elif operater == "in":
                expr = filtervalue in cellvalue
            else:
                expr = False

            if expr:
                tmp = rows.append(i)
        return rows

    def GetColValuesByColFilter(self, destinationcolumnname, filtercolumn, filtercolumnvalue, operater="=", wsobj=None):
        # This action is used to get all values on one column based on filter of another column
        columnvalues = []

        # get row index of filter column containing filter value
        rows = self.GetRowIndexesByFilter(filtercolumn, filtercolumnvalue, operater, wsobj)

        if len(rows) > 0:

            # get index of destination column
            descol = self.GetHeaderColumnIndex(destinationcolumnname, wsobj)
            for row in rows:
                # get value based on col index and row index
                value = self.GetCellValue(row, descol, wsobj)
                tmpvalues = columnvalues.append(value)
        return columnvalues

    def GetColValuesByFilterCols(self, destinationcolumnname, filtercolsdict, operater="=", wsobj=None):
        # This action is used to get all values on one column based on filter of another column
        columnvalues = []

        # get row index of filter column containing filter value
        listrows = []
        if len(filtercolsdict) > 0:
            for filtercolumn in filtercolsdict:
                filtercolvalue = filtercolsdict[filtercolumn]
                currentrows = []
                
                # [Nam Nguyen, 19-Dec-2018]: Modified script to search empty value
                # Including search empty value, not handle search empty or None value
                currentrows = self.GetRowIndexesByFilter(filtercolumn, filtercolvalue, operater, wsobj)
                
                # append to list
                tmp = listrows.append(currentrows)

        # if there are null list in, because of some value are wrong, will skip this filter
        if (len(listrows) > 0) and ([] not in listrows):

            # get common rows in list
            rows = list(reduce(lambda x, y: x & y, (set(i) for i in listrows)))

            # sort list
            tmp = rows.sort()

            # get index of destination column
            descol = self.GetHeaderColumnIndex(destinationcolumnname, wsobj)
            for row in rows:
                # get value based on col index and row index
                value = self.GetCellValue(row, descol, wsobj)
                tmpvalues = columnvalues.append(value)
        return columnvalues

class CSV():
    def __init__(self, csvfilepath, delimiter):        
        self.csvfilepath = csvfilepath
        self.delimiter = delimiter

    def open(self):        
        f = open(self.csvfilepath, "rb")
        csvobj = list(csv.reader(f, delimiter=self.delimiter))
        f.close()
        return csvobj
    
    def GetTotalRows(self, csvobj):
        return len(csvobj)
    
    def GetHeaderColumnName(self, csvobj):
        return csvobj[0]

    def GetHeaderColumnIndex(self, columnname, csvobj):
        try:
            headercolname = self.GetHeaderColumnName(csvobj)
            index = headercolname.index(columnname)
        except:
            index = -1
        return index

    def GetCellValue(self, row, col, csvobj):
        cellvalue = ""
        try:
            cellvalue = csvobj[row][col]
        except:
            cellvalue = ""
        return cellvalue

    def GetCellValueByColumnName(self, row, colname, csvobj):
        cellvalue = ""
        try:
            col = self.GetHeaderColumnIndex(colname, csvobj)
            cellvalue = csvobj[row][col]
        except:
            cellvalue = ""
        return cellvalue

    def GetColumnValues(self, colname, csvobj):
        colvalues = []
        try:
            col = self.GetHeaderColumnIndex(colname, csvobj)
            for rowvalue in csvobj:
                cellvalue = rowvalue[col]
                tmp = colvalues.append(cellvalue)
            # remove first data as header column name
            tmp = colvalues.remove(colname)
        except:
            colvalues = []
        return colvalues
    
    def GetRowIndexesByFilter(self, columnname, filtervalue, operater="=", csvobj=None):
        # this action is used to get list row index based on filter column value
        rows = []
        colindx = self.GetHeaderColumnIndex(columnname, csvobj)
        for i in xrange(1, len(csvobj)):
            cellvalue = self.GetCellValue(i, colindx, csvobj)
            expr = False
            if operater == "=":
                expr = filtervalue == cellvalue
            elif operater == "in":
                expr = filtervalue in cellvalue
            else:
                expr = False

            if expr:
                tmp = rows.append(i)
        return rows

    def GetColValuesByFilterCols(self, destinationcolumnname, filtercolsdict, operater="=", csvobj=None):        
        # This action is used to get all values on one column based on filter of another column
        columnvalues = []

        # get row index of filter column containing filter value
        listrows = []
        if len(filtercolsdict) > 0:            
            for filtercolumn in filtercolsdict:
                filtercolvalue = filtercolsdict[filtercolumn]                
                currentrows = []
                if filtercolvalue != None and filtercolvalue != "":                
                    currentrows = self.GetRowIndexesByFilter(filtercolumn, filtercolvalue, operater, csvobj)
            
                # append to list
                tmp = listrows.append(currentrows)

        # if there are null list in, because of some value are wrong, will skip this filter
        if (len(listrows) > 0) and ([] not in listrows):

            # get common rows in list
            rows = list(reduce(lambda x, y: x & y, (set(i) for i in listrows)))

            # sort list
            tmp = rows.sort()

            # get index of destination column
            descol = self.GetHeaderColumnIndex(destinationcolumnname, csvobj)
            for row in rows:
                # get value based on col index and row index
                value = self.GetCellValue(row, descol, csvobj)
                tmpvalues = columnvalues.append(value)
        return columnvalues
