config = {
    'exp_name' : 'hwdb-200',
    'epoch' : 200,
    'lr' : 1,
    'batch' : 600,
    'test_only' : False,
    'resume' : './history/hwdb/best_model.pth',
    'train_dataset' : '../dataset/HWDB1/train,../dataset/HWDB0/train',
    'test_dataset': '../dataset/HWDB1/seen,../dataset/HWDB0/seen',
    'imageH' : 32,
    'imageW' : 32,
    'encoder' : 'resnet',
    'decoder' : 'transformer',
    'alpha_path' : './data/char_hwdb_Chinese.txt',
    'radical_path': './data/radical_all_Chinese.txt',
    'decompose_path': './data/decompose.txt',
    'radical_model': './best_model.pth',
}
