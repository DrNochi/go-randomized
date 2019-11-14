import os
import tempfile

import h5py
import tensorflow as tf
from tensorflow import keras


def save_model_to_hdf5_group(model, f):
    tempfd, tempfname = tempfile.mkstemp(prefix='tmp-kerasmodel', suffix='.h5')

    try:
        os.close(tempfd)

        keras.models.save_model(model, tempfname)
        with h5py.File(tempfname, 'r') as serialized_model:
            serialized_model.copy('/', f, name='kerasmodel')
    finally:
        os.unlink(tempfname)


def load_model_from_hdf5_group(f):
    tempfd, tempfname = tempfile.mkstemp(prefix='tmp-kerasmodel', suffix='.h5')

    try:
        os.close(tempfd)

        with h5py.File(tempfname, 'w') as serialized_model:
            # serialized_model.copy(f['kerasmodel'], '/')
            root = f['kerasmodel']
            for attr_name, attr_value in root.attrs.items():
                serialized_model.attrs[attr_name] = attr_value
            for k in root.keys():
                f.copy(root[k], serialized_model, k)

        return keras.models.load_model(tempfname)
    finally:
        os.unlink(tempfname)


def set_gpu_memory_target(frac=None, total_memory=None, verbose=False):
    memory_limit = None
    if frac and total_memory:
        memory_limit = frac * total_memory

    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
                if memory_limit is not None:
                    tf.config.experimental.set_virtual_device_configuration(
                        gpu, [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=memory_limit)])
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            if verbose:
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(e)
