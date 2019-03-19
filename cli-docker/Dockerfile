FROM centos:7 as builder

ENV VAULT_VER=1.1.0

RUN yum install -y wget unzip
RUN wget -qO vault.zip https://releases.hashicorp.com/vault/${VAULT_VER}/vault_${VAULT_VER}_linux_amd64.zip
RUN unzip vault.zip

FROM centos:7

COPY --from=builder /vault /vault
RUN yum install -y epel-release
RUN yum install -y emacs vim nano python36

ADD files/get-pip.py /
RUN python36 get-pip.py
RUN pip3.6 install --index-url https://artifacts.kpn.org/api/pypi/pypi/simple --trusted-host artifacts.kpn.org py-de-vault
ADD files/requirements.txt /requirements.txt
RUN pip3.6 install -r requirements.txt

ADD files/provision-vault /provision-vault

CMD bash
