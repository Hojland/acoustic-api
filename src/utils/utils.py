import pandas as pd
from datetime import datetime
import sys
import logging
import pytz

import settings

LOGGING_FORMAT = "%(asctime)s :: %(filename)s :: %(funcName)s :: %(lineno)d :: %(message)s"
LOG_LEVEL = "INFO"

def pd_to_translate_dict(df: pd.DataFrame, col_from: str, col_to: str):
    translate_dct = dict(zip(df[col_from], df[col_to]))
    return translate_dct

def reverse_dummies(df: pd.DataFrame, join_cols: list, levels: list, name: str):
    df_dummy = df.set_index(join_cols)[levels]
    df_dummy = (
        df_dummy[df_dummy == 1]
        .stack()
        .reset_index()
        .drop(0, 1)
        .rename(columns={'level_' + str(len(join_cols)): name})
    )
    df = df.drop(levels, axis=1)
    df = pd.merge(df, df_dummy, on=join_cols)
    return df

def flatten_message(record):  # used to force logged messages to span a single line
    record["message"] = record["message"].replace("\r\n", "\\n").replace("\n", "\\n")

def time_now(local_tz: pytz.timezone):
    now = datetime.today().replace(tzinfo=pytz.utc).astimezone(tz=local_tz)
    return now

def setup_logging(log_name : str='/app/logs/hello.log'):
    #logger.remove()
    logging.basicConfig(filename=log_name, format=LOGGING_FORMAT, level=LOG_LEVEL, datefmt='%Y-%m-%d %H:%M:%S')
    #logging.basicConfig(filename=log_name, format=LOGGING_FORMAT, level=LOG_LEVEL, datefmt='%m/%d/%Y %I:%M:%S %p')

def get_logger(log_name: str='/app/logs/hello.log'):
    """Creates new logger.
    Args:
        model_name (str):
            Folder name for the logger to be saved in.
            Accepted values: 'ncf', 'implicit_model'
        model_dir (str): Name of the logger file.
    Returns:
        logger: Logger object.
    """

    def copenhagen_time(*args):
        """Computes and returns local time in Copenhagen.
        Returns:
            time.struct_time: Time converted to CEST.
        """
        _ = args  # to explicitly remove warning
        utc_dt = pytz.utc.localize(datetime.utcnow()) + timedelta(minutes=5, seconds=30)
        local_timezone = pytz.timezone("Europe/Copenhagen")
        converted = utc_dt.astimezone(local_timezone)
        return converted.timetuple()

    logging.Formatter.converter = copenhagen_time
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()

    # To files
    fh = logging.FileHandler(log_name)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)

    # to std out
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def multiple_replace(replace_dct: dict, text: str, **kwargs):
  # Create a regular expression  from the dictionary keys
  regex = re.compile("(%s)" % "|".join(map(re.escape, replace_dct.keys())), **kwargs)

  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: replace_dct[mo.string[mo.start():mo.end()]], text)

def mark_list_duplicates(lst: list):
    return [True if lst.count(col)>1 else False for col in lst]

def split_list(lst: list, chunk_size: int):
    return [lst[offs:offs+chunk_size] for offs in range(0, len(lst), chunk_size)]


def logical_operator_render(val1: str, val2: str, string_operator: str='=='):
    val1 = val1.replace(string_operator, '')
    val1 = float(val1)
    val2 = float(val2)
    if string_operator == '==' or string_operator == '=':
        return val2 == val1
    elif string_operator == '>=':
        return val2 >= val1
    elif string_operator == '<=':
        return val2 <= val1
    elif string_operator == '>':
        return val2 > val1
    elif string_operator == '<':
        return val2 < val1

    return NotImplementedError("this string operator isn't implemented")


def flatten_dict(d, sep="_"):
    obj = {}

    def recurse(t, parent_key=""):
        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k,v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t

    if isinstance(d, list):
        res_list = []
        for i in range(len(d)):
            recurse(d[i])
            res_list.append(obj.copy())
        return res_list
    else: 
        recurse(d)
    return obj

def dict_key_val_pair_eliminate(dct: dict, pair_id_re: str, key_id_re: str, val_id_re: str):
    out_dct = {}
    pair_dct = {}
    for k,v in dct.items():
        if re.search(key_id_re, k) and re.search(pair_id_re, k):
            pair_id = re.search(pair_id_re, k)[0]
            if pair_id in pair_dct:
                pair_dct[pair_id] = {v: pair_dct[pair_id]}
            else:
                pair_dct[pair_id] = v
        elif re.search(val_id_re, k) and re.search(pair_id_re, k):
            pair_id = re.search(pair_id_re, k)[0]
            if pair_id in pair_dct:
                pair_dct[pair_id] = {pair_dct[pair_id]: v}
            else:
                pair_dct[pair_id] = v
        else:
            out_dct[k] = v
    out_dct_pairs = {f"{k}_{paid_id}": v for paid_id, out_dct_pair in pair_dct.items() for k,v in out_dct_pair.items()}
    out_dct = {**out_dct, **out_dct_pairs}
    return out_dct

def dict_to_dict(d):
    def recurse(d):
        for k,v in d.items():
            if isinstance(v, dict):
                v = dict(v)
                v = recurse(v)
            else:
                pass
            d[k] = v
        return d

    if isinstance(d, dict):
        d = recurse(d)
    return dict(d)