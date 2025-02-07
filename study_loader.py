import numpy as np
import studies


'''
    Class to load data from earlier CPTu quick clay studies
    Studies are: 0: Valsson 2013 (unpublished); 1: Valsson, NGM 2016; 2: Valsson, IWLSC 2017 (Poster #9)

    transform function transforms data [ X, Y, Z ] to normalized coordinates:  X' = ( X - AVG(X) / STDEV(X)
    AVG(X) and STDEV(X) are either calculated average of training set, OR stored values if they are found
'''


class study_loader():
    def __init__( self, study_nr=2 ):

        # preset variables
        self.studies = [0,1,2,3]
        self.all_vars = [ # data we can return
            'D','U0','Sig_V','Sig_V_eff', # initial stress related
            'QC','QT','QQT','QN','QE','QTN','QTNT', # tip resistance related
            'FS','FT','RF','FR','FSN','FTNT', # sleeve frictional resistance related
            'U2','UT','DU','BQ','DUN','DUNT','UTN','UTNT' # pore water pressure resistance related
            ]

        # define class variables
        self.prep_var_info()

        # load/fit dataset
        self.load( study_nr=study_nr )        
        self.fit()



    def prep_var_info( self ):
        self.var_info = {}
        
        # init for all vars
        for some_var in self.all_vars:
            self.var_info[some_var] = { 'trans_vals' : None, 'ax_label' : '', 'log':False }

        # define specific dict entries
        labels = {
            'BQ': r'$B_q$' + ' = ' + r'$\frac{ \Delta u }{ q_n }$',
            'QQT': r'$Q_t$' + ' = ' + r"$\frac{ q_n }{ \sigma ' _{v0} }$",
            'FR': r'$F_r$' + ' = ' + r'$\frac{ f_s }{ q_n }$',
            'QTN': r'$q_{tn}$' + ' = ' + r"$\frac{ q_t }{ \sigma ' _{v0} }$",
            'FSN': r'$f_{sn}$' + ' = ' + r"$\frac{ f_s }{ \sigma ' _{v0} }$",
        }
        trans_vals = { # values from study_nr=2
            'BQ':  [  0.560, 0.350 ], #[  0.703, 0.323 ],
            'FR':  [  0.150, 0.160 ], #[  0.506, 0.230 ],
            'QQT': [  0.770, 0.300 ], #[  0.750, 0.308 ],
            'FSN': [ -1.080, 0.440 ], #[ -0.744, 0.356 ],            
            'QTN': [  0.900, 0.240 ], #[  0.885, 0.256 ],
        }

        logs ={
            'BQ':False,
            'FR':True,
            'FSN':True,
            'QQT':True,
            'QTN':True,
        }

        # overwrite
        for some_label in labels:
            self.var_info[some_label]['ax_label'] = labels[some_label]
        for some_label in trans_vals:
            self.var_info[some_label]['trans_vals'] = trans_vals[some_label]
        for some_label in logs:
            self.var_info[some_label]['log'] = logs[some_label]


    # validate user input
    def validate_study_nr( self, study_nr ):
        if study_nr in self.studies:
            return study_nr
        return self.studies[-1]


    # validate user input
    def validate_var_list( self, var_list ):
        if var_list is not None:
            for some_var in var_list:
                if some_var not in self.all_vars:
                    return None
            return var_list
        return None


    # loads data from different studies
    def load( self, study_nr=None ):
        self.study_nr = self.validate_study_nr( study_nr )

        self.study = studies.STUDY1 # always some data
        if self.study_nr==1:
            self.study = studies.STUDY2
        elif self.study_nr==2:
            self.study = studies.STUDY3
        elif self.study_nr==3:
            self.study = studies.STUDY4


    # not implemented - use to transform point cloud
    def transform( self, transform=True ):
        pass


    # retrieves (or calculates) scaling factors for standardscaler
    def trans_fact( self, var_id ):
        if self.var_info[self.var_list[var_id]]['trans_vals'] is None:
            print( 'no scaling info for: ' + self.var_list[var_id] + ')\nCalculating from data')
            
            # get all data
            n = 0
            all_vals = []
            for soil_type in self.study:
                n += len(soil_type[self.var_list[var_id]])
                all_vals += soil_type[self.var_list[var_id]]
            all_vals = np.array( all_vals )

            # apply logs
            if self.var_info[self.var_list[var_id]]['log']:
                all_vals = all_vals[all_vals>0] # only based on current value
                all_vals = np.log10( all_vals )

            n_ = len(all_vals)

            min_val, max_val = np.min(all_vals), np.max(all_vals)
            rng = max_val - min_val

            u = np.average( all_vals )
            m = np.median( all_vals )

            diff = np.round( (u-m)/rng*100, 2 )

            s = np.std( all_vals )

            self.var_info[self.var_list[var_id]]['trans_vals'] = [ u, s ]
            
            out = 'length: ' + str(n) + '/' + str(n_) + '\n'
            out += '  Setting: '
            out += 'u=' + str(round(u,4)) + '.'
            out += ' and s=' + str(round(s,4)) + '.'
            out +=  ' median: ' + str(round(m,4)) + '. diff: ' + str(diff) + '%\n\n'
            
            print( out )

        return self.var_info[self.var_list[var_id]]['trans_vals']


    # transform data coordinates (standard scaler)
    def trans_coord( self, var_id, coordlist ):
        # apply logs
        if self.var_info[self.var_list[var_id]]['log']:
            coordlist = np.log10( coordlist )


        u, s = self.trans_fact( var_id )
        coord_trans = coordlist - u # subtract mean
        coord_trans *= 1/s # divide by standard deviation
        return coord_trans


    # sets variable list to examine
    def fit( self, var_list=None):
        self.var_list = self.validate_var_list( var_list )

        if var_list==None:
            self.var_list = ['BQ','FSN','QTN'] # studies 2&3
            if self.study_nr == 0:
                self.var_list = ['BQ','FR','QQT']
        
        self.var_string = '_'.join(self.var_list)


    # adds data to the soil type dict
    def add_data( self, tmp_soil, soil_type, var_id, coord, log_mask ):
        tmp_soil[coord] = np.array( soil_type[self.var_list[var_id]] ) # original coordinates
        
        masked_coords = tmp_soil[coord][log_mask] # apply log_mask
        tmp_soil[coord + '_trans'] = self.trans_coord( var_id, masked_coords ) # transformed


    # calculate which points to ignore for negative logarithms (all components)
    def log_mask( self, soil_type ):
        log_mask = np.full(np.array(soil_type[self.var_list[0]]).shape, True) # all True

        for var in self.var_list: # for each variable
            if self.var_info[var]['log']: # that is log: remove values <=0
                log_mask = np.logical_and( log_mask, ( np.array(soil_type[var])>0 ) )
            #print('masked: ', np.sum(~log_mask))
        return log_mask


    # generates data-structure to return
    def data( self ):
        res = []

        for soil_type in self.study:
            # calc log_mask
            log_mask = self.log_mask( soil_type )

            tmp_soil = {} # each soil type placed in dict
            tmp_soil['id'] = soil_type['name']
            tmp_soil['color'] = ( soil_type['ColorR']/255,soil_type['ColorG']/255,soil_type['ColorB']/255)

            for var_id, coord in enumerate(['x', 'y', 'z']):
                tmp_soil['var' + coord] = self.var_list[var_id]
                tmp_soil['log' + coord] = self.var_info[self.var_list[var_id]]['log']
                tmp_soil[coord + 'label' ] = self.var_info[self.var_list[var_id]]['ax_label']
                self.add_data( tmp_soil, soil_type, var_id, coord, log_mask )

            res.append( tmp_soil )
        return res