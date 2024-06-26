from Utilz.training import predict, train_and_test, tune_and_train, time_previous_code, load_model_params
from Utilz.loads import get_custom_loss
from Utilz.data import CustomSequence
from Utilz.losses import calculate_and_visualize_mixed_MSE_metric
import logging
import torch
import torch.nn as nn
import os

from argparse import Namespace

from Analysis.analyze_reim import do_analysis


def main_function(
    args: Namespace,
    model: nn.Module,
    train_dataset: CustomSequence,
    val_dataset: CustomSequence,
    test_dataset: CustomSequence,
    model_dict: dict = None,
):
    custom_loss = get_custom_loss(args)

    if args.cpu_cores is not None:
        print(f"Setting number of CPU cores to {args.cpu_cores}")
        torch.set_num_threads(args.cpu_cores)
        torch.set_num_interop_threads(args.cpu_cores)

    if args.custom_code == 1:
        time_previous_code(test_dataset, args.load_in_gpu, None, args.batch_size)

    elif args.custom_code == 2:
        device = "cuda" if args.load_in_gpu else "cpu"
        model, _ = load_model_params(model, args.model_param_path, device)
        time_previous_code(test_dataset, args.load_in_gpu, model, args.batch_size)
    
    elif args.custom_code == 3:
        calculate_and_visualize_mixed_MSE_metric(args.output_dir, args.data_dir, args.model_save_name)

    elif args.do_analysis == 1:
        log_str = f"Analysis only mode for model {args.model}"
        print(log_str)
        logging.info(log_str)
        model_save_name = os.path.basename(args.model_param_path).split(".")[0]
        do_analysis(
            args.output_dir,
            args.data_dir,
            model_save_name,
            file_idx=args.analysis_file,
            item_idx=args.analysis_example,
        )

    elif args.do_prediction == 1:
        log_str = f"Prediction only mode for model {args.model}"
        print(log_str)
        logging.info(log_str)
        model_save_name = os.path.basename(args.model_param_path).split(".")[0]
        predict(
            model,
            model_param_path=args.model_param_path,
            test_dataset=test_dataset,
            output_dir=args.output_dir,
            model_save_name=model_save_name,
            batch_size=args.batch_size,
            verbose=args.verbose,
        )

        do_analysis(
            args.output_dir,
            args.data_dir,
            model_save_name,
            file_idx=args.analysis_file,
            item_idx=args.analysis_example,
        )

    else:
        # This assumes that `tune_train` and `train_model` have the same signature
        # (as in required arguments)
        if args.tune_train == 1:
            function_to_exec = tune_and_train
            print_str = f"Tune train mode for model {args.model}"
        else:
            function_to_exec = train_and_test
            print_str = f"Training mode for model {args.model}"

        print(print_str)
        logging.info(print_str)

        function_to_exec(
            model,
            args.model_save_name,
            args.num_epochs,
            custom_loss,
            args.epoch_save_interval,
            args.output_dir,
            train_dataset,
            val_dataset,
            test_dataset,
            args.verbose,
            data_dir=args.data_dir,
            batch_size=args.batch_size,
            analysis_file_idx=args.analysis_file,
            analysis_item_idx=args.analysis_example,
            model_param_path=args.model_param_path,
            model_dict=model_dict,
            learning_rate=args.lr,
            shuffle=args.shuffle,
        )
