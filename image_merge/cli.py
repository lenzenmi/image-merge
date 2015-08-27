import argparse
import os.path

from .core import (ImageFinder, TwoPerPage, ThreePerPage, FourPerPage, MaxHeightLandscape,
                   ImageCountError)


PER_PAGE = [TwoPerPage, ThreePerPage, FourPerPage]


def run(args):
    image_finder = ImageFinder(args.source)

    print()
    print('-' * 50)
    print('Found {} photo(s) in \'{}\''.format(
        image_finder.image_count,
        os.path.abspath(os.path.expanduser(args.source))
    ))
    print('-' * 50)
    dest = os.path.abspath(os.path.expanduser(args.dest))
    if os.path.exists(dest) and not os.path.isdir(dest):
        print('\'{}\' exists, but is not a folder'.format(dest))
        exit(1)
    elif not os.path.exists(dest):
        print('Making output directory: \'{}\''.format(dest))
        os.makedirs(dest, exist_ok=True)

    if args.count:
        output = PER_PAGE[args.count - 2](dest)
    elif args.max_height:
        output = MaxHeightLandscape(dest, args.max_height)

    output.add_image_finder(image_finder)

    print()
    print('running...')
    try:
        output.verify()
        output.run()
    except ImageCountError as e:
        print()
        print('WARNING:')
        print('-' * 50)
        print(e)
        print()
        yes_or_no = input('Do you want to continue?(y/n): ')
        if not yes_or_no.lower().startswith('y'):
            exit(1)
        else:
            output.run()

    except Exception as e:
        print()
        print('ERROR:')
        print('-' * 50)
        print(e)
        print()
        exit(1)


def main():
    parser = argparse.ArgumentParser(description='Combines multiple images into one for printing',
                                     prog='image-parser')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--count', '-c', type=int, choices=[2, 3, 4],
                       help='how many images per page')
    group.add_argument('--max-height',
                       help='maximum height in centimeters')
    parser.add_argument('source', help='path to the source files')
    parser.add_argument('dest', help='path where the final images will be saved')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    args = parser.parse_args()
    run(args)

if __name__ == '__main__':
    main()
