FROM public.ecr.aws/lambda/python:3.9

COPY gv3_grey.h5 /opt/ml/model.h5

RUN yum -y install tar gzip zlib freetype-devel \
    gcc \
    ghostscript \
    lcms2-devel \
    libffi-devel \
    libimagequant-devel \
    libjpeg-devel \
    libraqm-devel \
    libtiff-devel \
    libwebp-devel \
    make \
    openjpeg2-devel \
    rh-python36 \
    rh-python36-python-virtualenv \
    sudo \
    tcl-devel \
    tk-devel \
    tkinter \
    which \
    xorg-x11-server-Xvfb \
    zlib-devel \
    && yum clean all
  
COPY requirements.txt ./
RUN python3.9 -m pip install -r requirements.txt
# Install optimized pillow
RUN pip uninstall -y pillow && CC="cc -mavx2" pip install -U --force-reinstall pillow-simd

COPY app.py __init__.py helper.py ./

CMD ["app.lambda_handler"]
