import unittest
import pathlib
import os

import PIL.Image

from ..core import ImageFinder, TwoPerPage, ThreePerPage, FourPerPage, ImageCountError

OUTPUT_DIR = os.environ.get('IMAGE_MERGE_TEST_DIR')

if OUTPUT_DIR is None:
    OUTPUT_DIR = '/tmp/'


class testImageFinder(unittest.TestCase):

    IMAGE_DIR = (pathlib.Path(__file__).parent / 'images').as_posix()

    def test_image_count(self):
        image_finder = ImageFinder(self.IMAGE_DIR)
        self.assertEqual(image_finder.image_count, 1)

    def test_iter(self):
        image_finder = ImageFinder(self.IMAGE_DIR)
        count = 0
        for image in image_finder:
            self.assertIsInstance(image, PIL.Image.Image)
            count += 1

        self.assertEqual(count, 1)


class testTwoPerPage(unittest.TestCase):

    IMAGE_DIR = (pathlib.Path(__file__).parent / 'images').as_posix()

    def test_combine_two_per_page(self):
        image1 = ImageFinder(self.IMAGE_DIR)
        image2 = ImageFinder(self.IMAGE_DIR)
        output = TwoPerPage(OUTPUT_DIR, prefix='img2-')
        output.add_image_finder(image1)
        output.add_image_finder(image2)
        output.run()

    def test_bad_number_of_images(self):
        image1 = ImageFinder(self.IMAGE_DIR)
        output = TwoPerPage(OUTPUT_DIR, prefix='img2-')
        output.add_image_finder(image1)
        self.assertRaises(ImageCountError, output.run)


class testThreePerPage(unittest.TestCase):

    IMAGE_DIR = (pathlib.Path(__file__).parent / 'images').as_posix()

    def test_combine_three_per_page(self):
        image1 = ImageFinder(self.IMAGE_DIR)
        image2 = ImageFinder(self.IMAGE_DIR)
        image3 = ImageFinder(self.IMAGE_DIR)
        output = ThreePerPage(OUTPUT_DIR, prefix='img3-')
        output.add_image_finder(image1)
        output.add_image_finder(image2)
        output.add_image_finder(image3)
        output.run()

    def test_bad_number_of_images(self):
        image1 = ImageFinder(self.IMAGE_DIR)
        output = ThreePerPage(OUTPUT_DIR, prefix='img3-')
        output.add_image_finder(image1)
        self.assertRaises(ImageCountError, output.run)


class testFourPerPage(unittest.TestCase):

    IMAGE_DIR = (pathlib.Path(__file__).parent / 'images').as_posix()

    def test_combine_four_per_page(self):
        image1 = ImageFinder(self.IMAGE_DIR)
        image2 = ImageFinder(self.IMAGE_DIR)
        image3 = ImageFinder(self.IMAGE_DIR)
        image4 = ImageFinder(self.IMAGE_DIR)

        output = FourPerPage(OUTPUT_DIR, prefix='img4-')
        output.add_image_finder(image1)
        output.add_image_finder(image2)
        output.add_image_finder(image3)
        output.add_image_finder(image4)

        output.run()

    def test_bad_number_of_images(self):
        image1 = ImageFinder(self.IMAGE_DIR)
        output = FourPerPage(OUTPUT_DIR, prefix='img4-')
        output.add_image_finder(image1)
        self.assertRaises(ImageCountError, output.run)

if __name__ == '__main__':
    unittest.main()
