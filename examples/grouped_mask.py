import torch

torch.set_printoptions(profile="full", linewidth=256)
# torch.set_printoptions(profile="full")


def get_grouped_mask(mask, block_size, neg_inf):
    ori_shape = mask.shape
    assert(len(ori_shape) == 2)

    mask_group = torch.zeros((ori_shape[0] // block_size, ori_shape[1] // block_size), dtype=torch.float16)
    
    mask_tmp = mask.view(ori_shape[0] // block_size , block_size, ori_shape[1] // block_size, block_size)
    for i in range(seq_len // block_size):
        for j in range(seq_len // block_size):
            if torch.sum(mask_tmp[i,:,j,:]) == neg_inf * block_size * block_size:
                mask_group[i, j] = -1.0
            elif mask_tmp[i,:,j,:][-1, 0] == neg_inf:
                """
                    0,       0,     0 ..., 0, 0
                    -inf,    0,     0 ..., 0, 0
                    -inf, -inf,     0 ..., 0, 0                    
                    ...
                    -inf, -inf, -inf ..., -inf, 0
                """
                mask_group[i, j] = 1.0
            elif mask_tmp[i,:,j,:][0, -1] == neg_inf:
                """
                    -inf, -inf, -inf ..., -inf, -inf
                    0,    -inf, -inf ..., -inf, -inf
                    0,    0,    -inf ..., -inf, -inf                   
                    ...
                    0,    0,    0    ...,    0, -inf
                """
                mask_group[i, j] = 2.0
    return mask_group


if __name__ == "__main__":
    
    seq_len = 512
    n_init = 32
    n_local = 128
    _INF = -1.0
    block_size = 16

    mask = torch.zeros((seq_len, seq_len), dtype=torch.float16)
    for i in range(seq_len):
        mask[i,i+1:] = _INF
        if i > n_init + n_local:
            mask[i, n_init:i-n_local] = _INF

    mask_g = get_grouped_mask(mask, block_size, _INF)

    print(mask_g)
    """ result as:
    tensor([[ 2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2., -1.],
            [ 0.,  0., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2.]], dtype=torch.float16)

    """