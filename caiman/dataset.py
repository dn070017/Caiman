from typing import Optional, Union

import numpy as np
import pandas as pd

from caiman.utils import have_same_index, is_file, read_series

class Dataset:
    """Dataset

    Dataset for expression data used in Caiman.

    Parameters:
        xprs: Union[str, pandas.core.frame.DataFrame], required
            Path to the expression data or the expression dataframe. The data file
            should be formatted as follows: the rows should represent gene expression
            across all samples, and the columns should represent the expression profile
            of each sample. If provided  with dataframe, the index should be the genes
            and the columns should be the samples.

        groups: Union[str, pandas.core.series.Series], optional
            Path to the group information for each sample or the series data. The file
            should have two columns without any header. The first column should be the
            sample names, corresponds to the columns in xprs. The second column should
            be the group information for each sample. The two columns must be separated
            with <tab>. If provided with series, the index should be the sample names.

        **kargs: dict, optional
            Additional parameters passed to pandas.read_csv() to read xprs file.

    Attributes:
        xprs: pandas.core.frame.DataFrame
            Transposed expression dataframe with group information.

        groups: numpy.ndarray
            Unique groups.

        num_genes: int
            Number of genes in xprs dataframe.

        num_samples:
            Number of samples in xprs dataframe.

        num_groups:
            Number of unique groups.

    """
    def __init__(
        self,
        xprs: Union[str, pd.core.frame.DataFrame],
        groups: Union[str, pd.core.series.Series, None] = None,
        **kargs
    ) -> None:
        self.xprs: pd.DataFrame
        self.groups: np.ndarray
        self.num_genes: int
        self.num_samples: int
        self.num_groups: int

        if isinstance(xprs, pd.core.frame.DataFrame):
            self.xprs = xprs.transpose()
        elif is_file(xprs, 'xprs', error=True):
            self.xprs = pd.read_csv(xprs, **kargs).transpose()

        if (
            not isinstance(groups, pd.core.series.Series) and
            is_file(groups, 'groups', True)
        ):
            groups = read_series(groups, True)

        if (
            isinstance(groups, pd.core.series.Series) and
            have_same_index(groups, self.xprs, 'groups', 'xprs', True, True)
        ):
            groups = groups.loc[self.xprs.index]
        else:
            groups = pd.Series('NA', index=self.xprs.index)

        self.xprs.index = pd.MultiIndex.from_arrays([
            groups.values,
            self.xprs.index.values
        ]).set_names(['Group', 'Sample'])

        self.groups = groups.unique()
        self.num_groups = len(self.groups)
        self.num_samples, self.num_genes = self.xprs.shape

    def __repr__(self) -> str:
        return '<caiman.dataset.Dataset>'

    def __str__(self) -> str:
        str_groups = str(self.groups).replace('\n', f'\n{"":4}')
        message = ''.join((
            'Dataset\n\n',
            'Statistics\n',
            f'{"":4}number of samples: {self.num_samples}\n',
            f'{"":4}number of genes: {self.num_genes}\n',
            f'{"":4}number of groups: {self.num_groups}\n\n',
            'Groups\n',
            f'{"":4}{str_groups}\n'
        ))
        return message

    def get_xprs(
        self,
        group: Optional[str] = None,
        copy: bool = True
    ) -> pd.DataFrame:
        """Get the expression table of the given group

        Parameters:
            group: str, (optional)
                The group of expression the user wants to extract. If no group provided,
                return expression of all samples.

            copy: bool, default: True (optional)
                Return a deep copy instance of the expression dataframe (True) or return
                the reference of the original expression dataframe (False)

        Returns:
            pd.Dataframe
                Expression dataframe of the given group.

        """
        if group:
            index = self.xprs.index.get_level_values('Group') == group
        else:
            index = self.xprs.index

        if copy:
            return self.xprs.loc[index].copy()
        else:
            return self.xprs.loc[index]
