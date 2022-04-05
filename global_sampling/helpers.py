from tensorboardX import SummaryWriter
import torch.nn.functional as F
import torch
from sklearn.metrics import accuracy_score
import json

def log_model_weights(model, step, writer):
    for name, weight in model.named_parameters():
        writer.add_histogram(name, weight, step)
    writer.flush()

def log_hyper_configs(configs, step, writer):
    for client_id, hyper_config in enumerate(configs):
        writer.add_scalar('client_{}_learning_rate'.format(client_id), hyper_config['lr'], step)

def log_hyper_params(hyper_param_dict):
    to_be_persisted = {k: list(v) for k, v in hyper_param_dict.items()}
    with open('hyperparameters.json', 'w') as f:
        json.dump(to_be_persisted, f)

def compute_accuracy(logits, y):
    logits = torch.cat(logits)
    y = torch.cat(y)

    y_pred = F.softmax(logits, dim=1)
    y_pred = torch.argmax(y_pred, dim=1)

    y_pred = y_pred.cpu().detach().numpy()
    y = y.cpu().detach().numpy()

    return accuracy_score(y, y_pred)      

def get_hyperparameter_id(name, client_id):
    # hyperparameter-names must have format arbitrary_name_[round_number]
    # thus we cut off "_[round_number]" and add "client_[id]_" to obtain unique
    # log-id for each client such that each hyper-parameter configuration is 
    # logged in one time-diagram per client
    split_name = name.split('_')
    split_name = split_name[:-1]
    log_name = '_'.join(split_name)
    log_name = 'client_{}_'.format(client_id) + log_name
    return log_name

class ProtobufNumpyArray:
    """
        Class needed to deserialize numpy-arrays coming from flower
    """
    def __init__(self, bytes) -> None:
        self.ndarray = bytes