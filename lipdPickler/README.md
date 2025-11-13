# lipdPickler

* This repo underlies the lipdPickler container (docker pull davidedge/lipd_webapps:lipdPickler)

* The container requires a directory mounted with .lpd files to pickle

* The output requires a volume mount to receive 'lipd.pkl'

* with changes to match your path: docker run -v /root/query-container/output:/output -v /root/lipdPy/lipd.pkl:/lipd.pkl davidedge/lipd_webapps:lipdPickler
