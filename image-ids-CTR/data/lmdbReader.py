import lmdb
import six
import sys
import random
import torchvision.transforms as transforms

from PIL import Image
from torch.utils.data.sampler import Sampler
from torch.utils.data import Dataset

class lmdbDataset(Dataset):

    def __init__(self, root=None, transform=None, reverse=False, alphabet=None):
        self.env = lmdb.open(
            root,
            max_readers=1,
            readonly=True,
            lock=False,
            readahead=False,
            meminit=False)

        if not self.env:
            print('cannot creat lmdb from %s' % (root))
            sys.exit(0)

        with self.env.begin(write=False) as txn:
            nSamples = int(txn.get('num-samples'.encode()))
            self.nSamples = nSamples

        self.transform = transform
        self.reverse = reverse

    def __len__(self):
        return self.nSamples

    def __getitem__(self, index):
        if index > len(self):
            index = len(self) - 1
        assert index <= len(self), 'index range error index: %d' % index

        with self.env.begin(write=False) as txn:
            img_key = 'image-%09d' % index
            img_path = txn.get(img_key.encode())

            try:
                img = Image.open(img_path)
            except IOError:
                print('Corrupted image for %d' % index)
                return self[index + 1]

            label_key = 'label-%09d' % index
            label = str(txn.get(label_key.encode()).decode('utf-8'))

            label = strQ2B(label)
            label += '$'
            label = label.lower()
            if self.transform is not None:
                img = self.transform(img)
        return (img, label, index)

def strQ2B(ustring):
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring

class resizeNormalize(object):

    def __init__(self, size, test=False, interpolation=Image.BILINEAR):
        self.test = test
        self.size = size
        self.interpolation = interpolation
        self.toTensor = transforms.ToTensor()

    def __call__(self, img):
        width, height = img.size
        if 1.5 * width < height:
            img = img.transpose(Image.ROTATE_90)
        img = img.resize(self.size, self.interpolation)

        img = self.toTensor(img)
        img.sub_(0.5).div_(0.5)
        return img

class IndependentHalvesSampler(Sampler):
    def __init__(self, dataset, batch_size, iteration_num):

        len_dict = {}
        self.dataset = dataset
        self.batch_size = batch_size
        self.iteration_num = iteration_num

        for i in range(len(dataset)):
            img, label = dataset[i]
            if len(label) not in len_dict.keys():
                len_dict[len(label)] = [i]
            else:
                len_dict[len(label)].append(i)

        self.len_dict = len_dict

    def __iter__(self):
        batch = []
        assert (self.batch_size % 16 == 0)

        for i in range(self.iteration_num):
            for i in range(2, 10):
                list_index = self.len_dict[i]
                for j in range(2):
                    index = random.randint(0, len(list_index) - 1)
                    batch.append(list_index[index])
        return iter(batch)

    def __len__(self):
        return self.iteration_num * self.batch_size
