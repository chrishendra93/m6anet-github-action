import os
import torch
import toml
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from copy import deepcopy
from ..model.model import MILModel
from ..utils.builder import random_fn
from ..utils.data_utils import NanopolishDS, inference_collate
from ..utils.training_utils import inference
from torch.utils.data import DataLoader

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
NORM_PATH = os.path.join(ROOT_PATH, "model/norm_factors/norm_dict.joblib")
DEFAULT_MODEL_CONFIG =  os.path.join(ROOT_PATH, "model/configs/model_configs/1_neighbor/prod_pooling_summary_stats.toml")
DEFAULT_MODEL_WEIGHTS = os.path.join(ROOT_PATH, "model/model_states/summary_stats_pooling_pr_auc.pt")
MIN_READS = 20


def argparser():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument("--input_dir", default=None, required=True)
    parser.add_argument("--out_dir", default=None, required=True)
    parser.add_argument("--model_config", default=DEFAULT_MODEL_CONFIG)
    parser.add_argument("--model_state_dict", default=DEFAULT_MODEL_WEIGHTS)
    parser.add_argument("--batch_size", default=64, type=int)
    parser.add_argument("--num_workers", default=25, type=int)
    parser.add_argument("--num_iterations", default=1, type=int)
    parser.add_argument("--device", default='cpu', type=str)
    return parser


def run_inference(args):
    
    device = args.device
    num_workers = args.num_workers
    input_dir = args.input_dir
    out_dir = args.out_dir
    num_iterations = args.num_iterations
    batch_size = args.batch_size
    device = args.device
    model_config = toml.load(args.model_config)
    model_state_dict = torch.load(args.model_state_dict, map_location=torch.device(device))

    model = MILModel(model_config).to(device)
    model.load_state_dict(model_state_dict)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    ds = NanopolishDS(input_dir, MIN_READS, NORM_PATH, mode='Inference')
    dl = DataLoader(ds, num_workers=num_workers, collate_fn=inference_collate, batch_size=batch_size, worker_init_fn=random_fn, shuffle=False)
    result_df = ds.data_info[["transcript_id", "transcript_position", "n_reads"]].copy(deep=True)   
    results = inference(model, dl, device, num_iterations)
    result_df["probability_modified"] = results 
    result_df.to_csv(os.path.join(out_dir, "data.result.csv"), index=False)

def main():
    args = argparser().parse_args()
    run_inference(args)


if __name__ == '__main__':
    main()
