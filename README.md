## Introduction

This is the implementation of our paper: "On Disambiguating Authors: An Incremental Approach Based on Collaboration Network."

## Requirements

- python 3.6.0
- numpy 1.14.0
- networkx 1.11
- gensim 3.2.0
- pymysql 0.9.2

We run all the experiments on a 2.1 GHz machine with 156GB memory running Linux operating system. 


## Download dataset and preprocess

Example dataset are available on [data](https://pan.baidu.com/s/1bowUE7Nw23B6HA-_l7btew). 

Our data are saved in mysql database, the encoding is "UTF8", you can import those sql files directly (Our mysql version is 5.7).


## How to run

```Bash
cd $project_path

# fp-growth
# this step can be ignored beacuse the fp-items results has been contained in the data link.
cd generate_fp_items
nohup python3 -u generate_fps.py >log_fp.txt 2>&1 &

# scn 
cd ../scn_build
nohup python3 -u build_network.py >log_scn.txt 2>&1 &

# gcn
cd ../gcn_build/
nohup python3 -u gcn.py >log_gcn.txt 2>&1 &

# incremental
cd ../incremental/
nohup python3 -u incremental.py >log_incremental.txt 2>&1 &
```

The output data format is as following:

```
a 1    p1,p2,p3
a 2    p4,p5
```
Where, "a" is the name, "a 1" is one real author named "a", "p1,p2,p3" are papers of author "a 1". Especially, authors with one paper are not saved into the output file, those data are processed in the code of next step.

**Note:** Due to larger-scale dataset, data in this demo are sampled from original data which are smaller than what we used in the paper, so the performance is lower than reported performance.