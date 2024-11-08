import torch
import torch.nn as nn
from torchvision.utils import save_image
import os
import sys
import tqdm
import argparse
import matplotlib.pyplot as plt
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from dataloader import Test_Loader
from Restormer.model import Restormer, RestormerLocal
from utils.utils import calc_psnr, same_seed, count_parameters, tensor2cv, AverageMeter, judge_and_remove_module_dict


@torch.no_grad()
def predict(model, args, device):
    model.eval()

    if args.dataset == 'GoPro+HIDE':
        dataset_name = ['GoPro', 'HIDE']
    else:
        dataset_name = [args.dataset]

    for val_dataset_name in dataset_name:
        # dataset_path = os.path.join(args.data_path, val_dataset_name)
        dataset_path = args.data_path + '/' + val_dataset_name
        
        # Ensure the dataset path exists
        assert os.path.exists(dataset_path), f"Dataset path {dataset_path} does not exist."

        dataset = Test_Loader(data_path=dataset_path,
                                crop_size=args.crop_size,
                                ZeroToOne=False)
        
        # Ensure the dataset is not empty
        assert len(dataset) > 0, f"Dataset at {dataset_path} is empty."

        save_dir = os.path.join(args.dir_path, 'results', f'{val_dataset_name}')
        os.makedirs(save_dir, exist_ok=True)
        dataset_len = len(dataset)
        tq = tqdm.tqdm(range(dataset_len))
        tq.set_description(f'Predict {val_dataset_name}')

        for idx in tq:
            sample = dataset[idx]
            assert 'blur' in sample, f"Sample at index {idx} does not contain 'blur' key."
            input = sample['blur'].unsqueeze(0).to(device)
            b, c, h, w = input.shape
            factor = 8
            h_n = (factor - h % factor) % factor
            w_n = (factor - w % factor) % factor
            input = torch.nn.functional.pad(input, (0, w_n, 0, h_n), mode='reflect')

            output = model(input)
            output = output[:, :, :h, :w]
            output = output.clamp(-0.5, 0.5)

            image_name = os.path.split(dataset.get_path(idx=idx)['blur_path'])[-1]
            save_img_path = os.path.join(save_dir, image_name)

            save_image(output.squeeze(0).cpu() + 0.5, save_img_path)
            print(f"Saved image {save_img_path}")


if __name__ == "__main__":
    # hyperparameters
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", default=1, type=int)
    parser.add_argument("--data_path", default='content/ID_Blau/dataset/test', type=str)
    parser.add_argument("--dir_path", default='content/ID_Blau/out/Restormer', type=str)
    parser.add_argument("--model_path", default=None, type=str)
    parser.add_argument("--model", default='Restormer', type=str, choices=['Restormer', 'RestormerLocal'])
    parser.add_argument("--dataset", default='GoPro+HIDE', type=str, choices=['GoPro+HIDE', 'GoPro', 'HIDE', 'RealBlur_J', 'RealBlur_R', 'RWBI'])
    parser.add_argument("--crop_size", default=None, type=int)

    args = parser.parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device :", device)

    # Ensure the dataset path exists
    assert os.path.exists(args.data_path), f"Dataset path {args.data_path} does not exist."

    # Ensure the model path exists
    assert os.path.exists(args.model_path), f"Model path {args.model_path} does not exist."

    if not os.path.isdir(args.dir_path):
        os.makedirs(args.dir_path)

    # Model and optimizer
    if args.model == 'Restormer':
        net = Restormer()
    elif args.model == 'RestormerLocal':
        net = RestormerLocal()
    else:
        raise ValueError("model must be Restormer or RestormerLocal")
    
    load_model_state = torch.load(args.model_path)
    assert load_model_state is not None, "Failed to load model state."

    if 'model_state' in load_model_state.keys():
        load_model_state["model_state"] = judge_and_remove_module_dict(load_model_state["model_state"])
        net.load_state_dict(load_model_state["model_state"])
    elif 'model' in load_model_state.keys():
        load_model_state["model"] = judge_and_remove_module_dict(load_model_state["model"])
        net.load_state_dict(load_model_state["model"])
    elif 'params' in load_model_state.keys():
        load_model_state["params"] = judge_and_remove_module_dict(load_model_state["params"])
        net.load_state_dict(load_model_state["params"])
    else:
        load_model_state = judge_and_remove_module_dict(load_model_state)
        net.load_state_dict(load_model_state)

    net = nn.DataParallel(net)
    net.to(device)

    # Ensure the model is on the correct device
    assert next(net.parameters()).is_cuda, "Model is not on CUDA device."

    print("device:", device)
    print(f'args: {args}')
    print(f'model parameters: {count_parameters(net)}')

    same_seed(2023)
    predict(net, args=args, device=device)