import tarfile

with tarfile.open('./template.tar', "w") as tar:
    tar.add('./template', arcname = '', recursive = True)