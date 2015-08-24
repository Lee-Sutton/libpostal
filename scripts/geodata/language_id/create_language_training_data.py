import argparse
import logging
import os
import subprocess
import sys

this_dir = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.realpath(os.path.join(os.pardir, os.pardir)))

from geodata.osm.osm_address_training_data import WAYS_LANGUAGE_DATA_FILENAME, ADDRESS_LANGUAGE_DATA_FILENAME

LANGUAGES_ALL_FILE = 'languages.all'
LANGAUGES_RANDOM_FILE = 'languages.random'
LANGUAGES_TRAIN_FILE = 'languages.train'
LANGUAGES_CV_FILE = 'languages.cv'
LANGUAGES_TEST_FILE = 'languages.test'


def create_language_training_data(osm_dir, split_data=True, train_split=0.8, cv_split=0.1):
    language_all_path = os.path.join(osm_dir, LANGUAGES_ALL_FILE)

    ways_path = os.path.join(osm_dir, WAYS_LANGUAGE_DATA_FILENAME)

    addresses_path = os.path.join(osm_dir, ADDRESS_LANGUAGE_DATA_FILENAME)

    if os.system(' '.join(['cat', ways_path, '>', language_all_path])) != 0:
        raise SystemError('Could not find {}'.format(ways_path))

    if os.system(' '.join(['cat', addresses_path, '>>', language_all_path])) != 0:
        raise SystemError('Could not find {}'.format(addresses_path))

    languages_random_path = os.path.join(osm_dir, LANGAUGES_RANDOM_FILE)

    if os.system(u' '.join(['shuf', '--random-source=/dev/urandom', language_all_path, '>', languages_random_path])) != 0:
        raise SystemError('shuffle failed')

    languages_train_path = os.path.join(osm_dir, LANGUAGES_TRAIN_FILE)

    if split_data:
        languages_test_path = os.path.join(osm_dir, LANGUAGES_TEST_FILE)

        subprocess.check_call(['split -l $[ $(wc -l', languages_random_path, '| cut -d" " -f1) *', int(train_split * 100), '/ 100 + 1 ]', languages_random_path])
        subprocess.check_call(['mv xaa', languages_train_path])
        subprocess.check_call(['mv xab', languages_test_path])

        cv_split = cv_split / (1 - (cv_split + train_split))
        languages_cv_path = os.path.join(osm_dir, LANGUAGES_CV_FILE)

        subprocess.check_call(['split -l $[ $(wc -l', languages_test_path, '| cut -d" " -f1) *', int(cv_split * 100), '/ 100 + 1 ]', languages_test_path])
        subprocess.check_call(['mv', 'xaa', languages_cv_path])
        subprocess.check_call(['mv', 'xab', languages_test_path])
    else:
        subprocess.check_call(['mv', languages_random_path, languages_train_path])

if __name__ == '__main__':
    # Handle argument parsing here
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--no-split',
                        action='store_false',
                        default=True,
                        help='Do not split data into train/cv/test')

    parser.add_argument('-t', '--train-split',
                        type=float,
                        default=0.8,
                        help='Train split percentage as a float (default 0.8)')

    parser.add_argument('-c', '--cv-split',
                        type=float,
                        default=0.1,
                        help='Cross-validation split percentage as a float (default 0.1)')

    parser.add_argument('-o', '--osm-dir',
                        default=os.getcwd(),
                        help='OSM directory')

    args = parser.parse_args()
    if args.train_split + args.cv_split >= 1.0:
        raise ValueError('Train split + cross-validation split must be less than 1.0')

    if not os.path.exists(args.osm_dir):
        raise ValueError('OSM directory does not exist')

    create_language_training_data(args.osm_dir, split_data=args.no_split, train_split=args.train_split, cv_split=args.cv_split)
