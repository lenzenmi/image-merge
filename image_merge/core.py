import pathlib
import os.path
import math
import decimal

from PIL import Image


class ImageMergeError(Exception):
    pass


class ImageCountError(ImageMergeError):
    pass


class ImageSizeError(ImageMergeError):
    pass


class ImageFinder:
    def __init__(self, path):
        '''
        Locates image files within ``path``
        :param str path: The path of the folder to look in
        '''
        self._path = pathlib.Path(os.path.expanduser(path))
        if not self._path.is_dir():
            raise ValueError('{} must be a directory'.format('path'))

        self._image_count = 0
        self._count_images()

    def __iter__(self):
        for path in self._path.iterdir():
            if not path.match('.*') and path.is_file():
                yield Image.open(str(path.absolute()))

    @property
    def image_count(self):
        return self._image_count

    def _count_images(self):
        for file_ in self._path.iterdir():
            if not file_.match('.*') and file_.is_file():
                Image.open(str(file_.absolute()))
                self._image_count += 1


class BaseOutputImage:
    '''
    Subclass this class to make different page layouts.

    You must set the following class variables::

        IMAGES_PER_PAGE
        BOXES

    The ``setup_page`` method can be overriden to perform calculations and
    set the above variables.

    To use, first add an ``ImageFinder`` using the ``add_image_finder`` method,
    then call the ``run`` method.


    '''
    IMAGES_PER_PAGE = 0  # must set in each subclass

    def __init__(self, path, prefix='img-', count=1, width=1800, height=1200, border=10,
                 format_='JPEG', mode='RGB', quality=95, background_colour=(0xFF, 0xFF, 0xFF),
                 dpi=(300, 300), progressive=False):
        '''
        Base Output Image. Most params equate to PIL.Image.New

        Subclasses need to impliment the ``run`` method

        :param str path: base directory for the new image
        :param str prefix: prefix to start output image with
        :param int count: the count of the first output image
        '''
        self.width = width
        self.height = height
        self.border = border
        self.format_ = format_
        self.mode = mode
        self.quality = quality
        self.background_colour = background_colour
        self.dpi = dpi
        self.progressive = progressive

        self.count = 0
        if isinstance(path, pathlib.PurePath):
            self.path = path
        else:
            self.path = pathlib.Path(os.path.expanduser(path))

        self.prefix = prefix
        self.images = []

    def setup_page(self):
        '''
        Called once per ``run`` method. Should be overriden to perform calculations
        and setup page variables such as ``BOXES``

        The ``BOXES`` variable should contain an iterable of tuples. Each tuple represents
        the top left location for a pasted sub image. The number of tuples is equal to the
        number of sub-images per page which is equal to ``IMAGES_PER_PAGE``
        eg for a 2 page layout. The first image starts at the top left corner,
        the second starts 20px to the right::

            BOXES = [(0, 0), (20, 0)]
        '''
        self.BOXES = []

    def add_image_finder(self, image_finder):
        '''
        Add input images to be transformed. Can be called multiple times to add additional images.

        :param image_finder: Expects an initiated ``ImageFinder`` or list/tuple of ``ImageFinder``s
        '''
        if isinstance(image_finder, (list, tuple)):
            self.images.extend(image_finder)
        else:
            self.images.append(image_finder)

    def verify(self):
        '''
        Verifies that the number of loaded images is a multiple of ``IMAGES_PER_PAGE``

        :raises: ImageCountError
        '''
        input_count = sum([img.image_count for img in self.images])
        if not input_count % self.IMAGES_PER_PAGE == 0:
            raise ImageCountError("{} is not a multiple of {}".format(input_count,
                                                                      self.IMAGES_PER_PAGE))

    def run(self):
        '''
        Combines images into single pages.
        '''
        self.setup_page()
        input_images = [None for _ in range(self.IMAGES_PER_PAGE)]

        index = 0
        while self.images:
            image_finder = self.images.pop()
            for image in image_finder:
                while index < len(input_images):
                    input_images[index] = image
                    index += 1
                    if index < len(input_images):
                        break
                    else:
                        # we have a full page, combine them
                        self._combine_images(input_images)
                        # reset for next page
                        input_images = [None for _ in range(self.IMAGES_PER_PAGE)]
                        index = 0
                        break

        leftover_images = tuple(filter(None, input_images))
        if leftover_images:
            self._combine_images(leftover_images)

    def _new_page(self):
        '''
        Generates a new in-memory image
        '''
        self.image = Image.new(mode=self.mode, size=(self.width, self.height),
                               color=self.background_colour)

    def _save(self):
        '''
        saves the in-memory image to disk
        '''
        file_name = self.path / '{}{:04}'.format(self.prefix, self.count)
        file_name = file_name.with_suffix('.jpg')
        self.count += 1
        self.image.save(str(file_name.absolute()), format=self.format_,
                        progressive=self.progressive,
                        dpi=self.dpi, quality=self.quality)

    def _transform(self, image):
        # test for the longest side.
        x, y = image.size
        if (((self.BOX_HEIGHT > self.BOX_WIDTH) and (x > y)) or
                (self.BOX_WIDTH > self.BOX_HEIGHT) and (y > x)):
            image = image.transpose(Image.ROTATE_90)
            x, y = image.size

        # if it's the right size, we are done
        if x == self.BOX_WIDTH and y == self.BOX_HEIGHT:
            return image

        # enlarge if too small
        if (x < self.BOX_WIDTH and
                y < self.BOX_HEIGHT):
            x_ratio = self.BOX_WIDTH / x
            y_ratio = self.BOX_HEIGHT / y
            min_ratio = min(x_ratio, y_ratio)
            new_x = math.ceil(x * min_ratio)
            new_y = math.ceil(y * min_ratio)
            image = image.resize((new_x, new_y), Image.LANCZOS)

        # shrink if too large
        image.thumbnail((self.BOX_WIDTH, self.BOX_HEIGHT), Image.LANCZOS)

        return image

    def _centre_image(self, image, box):
        x, y = image.size

        delta_x = (self.BOX_WIDTH - x) // 2
        delta_y = (self.BOX_HEIGHT - y) // 2

        return (box[0] + delta_x, box[1] + delta_y)

    def _combine_images(self, images):
        '''
        Creates a new image, resizes the images passed in, and pastes them into position
        according to the ``BOXES`` static variable.

        :param images: a list of opened image objects to be combined into a single image
        '''
        transformed_images = []
        for image in images:
            transformed_images.append(self._transform(image))
        self._new_page()
        index = 0
        while index < len(transformed_images):
            self.image.paste(transformed_images[index],
                             self._centre_image(transformed_images[index], self.BOXES[index]))
            index += 1

        # save the combined image
        self._save()

        # clean up
        for image in images:
            image.close()
        self.image.close()


class TwoPerPage(BaseOutputImage):
    IMAGES_PER_PAGE = 2

    def setup_page(self):
        '''
        Sets the variables that define the page layout
        '''
        self.BOX_WIDTH = (self.width - (3 * self.border)) // self.IMAGES_PER_PAGE
        self.BOX_HEIGHT = (self.height - (2 * self.border))
        self.BOX_ONE = (self.border, self.border)
        self.BOX_TWO = (2 * self.border + self.BOX_WIDTH, self.border)
        self.BOXES = [self.BOX_ONE, self.BOX_TWO]


class ThreePerPage(BaseOutputImage):
    IMAGES_PER_PAGE = 3

    def setup_page(self):
        '''
        Sets the variables that define the page layout
        '''
        self.BOX_WIDTH = (self.width - (4 * self.border)) // self.IMAGES_PER_PAGE
        self.BOX_HEIGHT = (self.height - (2 * self.border))
        self.BOX_ONE = (self.border, self.border)
        self.BOX_TWO = (2 * self.border + self.BOX_WIDTH, self.border)
        self.BOX_THREE = (3 * self.border + 2 * self.BOX_WIDTH, self.border)
        self.BOXES = [self.BOX_ONE, self.BOX_TWO, self.BOX_THREE]


class FourPerPage(BaseOutputImage):
    IMAGES_PER_PAGE = 4

    def setup_page(self):
        '''
        Sets the variables that define the page layout
        '''
        self.BOX_WIDTH = (self.width - (3 * self.border)) // 2
        self.BOX_HEIGHT = (self.height - (3 * self.border)) // 2
        self.BOX_ONE = (self.border, self.border)
        self.BOX_TWO = (2 * self.border + self.BOX_WIDTH, self.border)
        self.BOX_THREE = (self.border, 2 * self.border + self.BOX_HEIGHT)
        self.BOX_FOUR = (2 * self.border + self.BOX_WIDTH, 2 * self.border + self.BOX_HEIGHT)
        self.BOXES = [self.BOX_ONE, self.BOX_TWO, self.BOX_THREE, self.BOX_FOUR]


class MaxHeightLandscape(BaseOutputImage):
    def __init__(self, path, max_height, **kwargs):
        '''
        max_height is the maximum image height in cm
        '''
        super(MaxHeightLandscape, self).__init__(path, **kwargs)
        pixels_per_inch = self.dpi[1]
        inches_per_cm = decimal.Decimal(1) / decimal.Decimal('2.54')
        # convert max_height into pixels
        self.max_height = decimal.Decimal(max_height) * inches_per_cm * pixels_per_inch

    def verify(self):
        '''
        Checks to make sure the maximum image height is less than the output image height

        :raises: ImageSizeError
        '''
        img_height = self.max_height + (2 * self.border)
        if img_height > self.height:
            raise ImageSizeError('max-height is larger than the paper size')

    def setup_page(self, horizontal_offset=0):
        self.BOX_WIDTH = (self.width - horizontal_offset) - (2 * self.border)
        self.BOX_HEIGHT = (self.max_height)
        self.BOX = ((self.border + horizontal_offset), self.border)

    def run(self):
        '''
        Resizes to images to a maximum height. Tries to fit multiple images per page.
        '''
        horizontal_offset = 0
        self.setup_page(horizontal_offset)
        self._new_page()

        while self.images:
            image_finder = self.images.pop()
            for image in image_finder:
                transformed_image = self._transform(image)
                horizontal_offset = horizontal_offset + self.border + transformed_image.size[0]
                if horizontal_offset > (self.width - self.border):
                    self._save()
                    self.image.close()
                    horizontal_offset = 0
                    self.setup_page(horizontal_offset)
                    self._new_page()
                self.image.paste(transformed_image, self._centre_image(transformed_image, self.BOX))
                self.setup_page(horizontal_offset)

        self._save()
        self.image.close()

    def _transform(self, image):

        x, y = image.size

        # if it's the right size, we are done
        if y == self.BOX_HEIGHT:
            return image

        # enlarge if too small
        if (y < self.BOX_HEIGHT):
            y_ratio = self.BOX_HEIGHT / y
            new_x = math.ceil(x * y_ratio)
            new_y = math.ceil(y * y_ratio)
            image = image.resize((new_x, new_y), Image.LANCZOS)

        # shrink if too large
        image.thumbnail(((self.width - 2 * self.border), self.BOX_HEIGHT), Image.LANCZOS)

        return image

    def _centre_image(self, image, box):
        _, y = image.size

        delta_x = 0  # only center vertically
        delta_y = (self.height - (2 * self.border) - y) // 2

        return (box[0] + delta_x, box[1] + delta_y)
