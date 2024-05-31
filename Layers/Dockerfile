FROM amazonlinux:1
WORKDIR /
RUN yum update -y
# Install required libraries for OpenCV
RUN yum install -y \
    libglvnd-glx \
    libglvnd-opengl \
    libXi \
    libXrender \
    libXrandr \
    libXtst \
    libXfixes \
    mesa-libGL \
    mesa-libGLU \
    glibc \
    gcc \
    openssl-devel \
    wget \
    tar
# Install Python 3.9.0
RUN wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz
RUN tar -xzvf Python-3.9.0.tgz
WORKDIR /Python-3.9.0
RUN ./configure --enable-optimizations
RUN make install
# Install Python packages
RUN mkdir /packages
RUN echo "opencv-python-headless" >> /packages/requirements.txt
RUN mkdir -p /packages/opencv-python-3.9/python/lib/python3.9/site-packages
RUN pip3.9 install -r /packages/requirements.txt -t /packages/opencv-python-3.9/python/lib/python3.9/site-packages

