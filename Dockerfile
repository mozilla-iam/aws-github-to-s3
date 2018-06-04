FROM lambci/lambda:build-python2.7

RUN git clone https://github.com/libgit2/libgit2.git
RUN cd libgit2 && cmake . && make && make install
