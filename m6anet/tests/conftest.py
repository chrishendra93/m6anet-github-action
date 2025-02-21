import os
import pytest
import json
import numpy as np
from m6anet.scripts.constants import M6A_KMERS, NUM_NEIGHBORING_FEATURES


@pytest.fixture
def eventalign_fpath():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "data/eventalign.txt")


@pytest.fixture
def eventalign_index():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "data/eventalign.index")


@pytest.fixture
def data_info():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "data/data.info")


@pytest.fixture
def data_json():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "data/data.json")


@pytest.fixture
def dataprep_args(eventalign_fpath, tmp_path):
    return {
            'eventalign': eventalign_fpath,
            'out_dir': tmp_path,
            'chunk_size': 1000000,
            'readcount_min': 1,
            'readcount_max': 1000,
            'min_segment_count': 1,
            'n_neighbors': NUM_NEIGHBORING_FEATURES,
            'n_processes': 4
            }


class DataprepHelpers:

    @staticmethod
    def is_equal_data(sorted_idx1, sorted_idx2, json_fpath1, json_fpath2):
        with open(json_fpath1, 'r') as f, \
            open(json_fpath2, 'r') as g:
            for row1, row2 in zip(sorted_idx1.iterrows(), sorted_idx2.iterrows()):
                kmer1, read_ids1, features1 = DataprepHelpers.read_json_from_idx_row(row1, f)
                kmer2, read_ids2, features2 = DataprepHelpers.read_json_from_idx_row(row2, g)

                assert(features1.shape == features2.shape)
                assert(kmer1 == kmer2)

                sort_idx1 = np.argsort(read_ids1)
                sort_idx2 = np.argsort(read_ids2)

                if not np.allclose(read_ids1[sort_idx1], read_ids2[sort_idx2]):
                    return False
                if not np.allclose(features1[sort_idx1], features2[sort_idx2]):
                    return False
        return True

    @staticmethod
    def read_json_from_idx_row(row_info, json_file):
        _, row = row_info
        tx_id, tx_pos, start_pos, end_pos = row[["transcript_id", "transcript_position",
                                                "start", "end"]]
        json_file.seek(start_pos, 0)
        json_str = json_file.read(end_pos - start_pos)
        pos_info = json.loads(json_str)[tx_id][str(tx_pos)]

        assert(len(pos_info.keys()) == 1)

        kmer, features = list(pos_info.items())[0]
        features = np.array(features)
        read_ids, features = features[:, -1].astype('int'), features[:, :-1]
        return kmer, read_ids, features

@pytest.fixture
def dataprep_helpers():
    return DataprepHelpers
