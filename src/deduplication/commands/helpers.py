import os

import pandas as pd
from tqdm import tqdm

from duplicatefinder.KDTreeFinder import KDTreeFinder
from duplicatefinder.cKDTreeFinder import cKDTreeFinder
from utils.FileSystemUtils import FileSystemUtils


def copy_images(df_results, output_path_in, column):
    """
    Copy the images into folders.
    :param df_results:
    :param output_path_in:
    :param column:
    :return:
    """
    with tqdm(total=len(df_results)) as pbar:
        for index, row in df_results.iterrows():
            full_file_name = row[column]

            dest_path = os.path.join(output_path_in, column)

            FileSystemUtils.mkdir_if_not_exist(dest_path)
            FileSystemUtils.copy_file(full_file_name, dest_path)
            pbar.update(1)


def save_results(img_file_list_in, to_keep_in, to_remove_in, hash_size_in, threshold_in, output_path_in,
                 delete_keep_in=False):
    if len(to_keep_in) > 0:
        to_keep_path = os.path.join(output_path_in,
                                    "duplicates_keep_" + str(hash_size_in) + "_dist" + str(threshold_in) + ".csv")

        duplicates_keep_df = pd.DataFrame(to_keep_in)
        duplicates_keep_df.columns = ['keep']
        duplicates_keep_df['hash_size'] = hash_size_in
        duplicates_keep_df['threshold'] = threshold_in
        duplicates_keep_df.to_csv(to_keep_path, index=False)
        copy_images(duplicates_keep_df, output_path_in, 'keep')

    if len(to_remove_in) > 0:
        to_remove_path = os.path.join(output_path_in,
                                      "duplicates_remove_" + str(hash_size_in) + "_dist" + str(threshold_in) + ".csv")
        duplicates_remove_df = pd.DataFrame(to_remove_in)
        duplicates_remove_df.columns = ['remove']
        duplicates_remove_df['hash_size'] = hash_size_in
        duplicates_remove_df['threshold'] = threshold_in
        duplicates_remove_df.to_csv(to_remove_path, index=False)
        copy_images(duplicates_remove_df, output_path_in, 'remove')

    if len(to_remove_in) > 0:
        survived_path = os.path.join(output_path_in,
                                     "survived_df" + str(hash_size_in) + "_dist" + str(threshold_in) + ".csv")
        if delete_keep_in:
            survived = list(set(img_file_list_in).difference(set(to_keep_in + to_remove_in)))
        else:
            survived = list(set(img_file_list_in).difference(set(to_remove_in)))
        print('We have found {0}/{1} not duplicates in folder'.format(len(survived), len(img_file_list_in)))
        survived_df = pd.DataFrame(survived)
        survived_df.columns = ['survived']
        survived_df['hash_size'] = hash_size_in
        survived_df['threshold'] = threshold_in
        survived_df.to_csv(survived_path, index=False)
        copy_images(survived_df, output_path_in, 'survived')


def build_tree(df_dataset, tree_type, distance_metric_in, leaf_size_in, parallel_in, batch_size_in):
    if tree_type == 'cKDTree':
        near_duplicate_image_finder = cKDTreeFinder(df_dataset, distance_metric=distance_metric_in,
                                                    leaf_size=leaf_size_in,
                                                    parallel=parallel_in, batch_size=batch_size_in)
    elif tree_type == 'KDTree':
        near_duplicate_image_finder = KDTreeFinder(df_dataset, distance_metric=distance_metric_in,
                                                   leaf_size=leaf_size_in,
                                                   parallel=parallel_in, batch_size=batch_size_in)

    return near_duplicate_image_finder
