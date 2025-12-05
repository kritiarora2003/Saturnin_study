% ============================================================
% Toy Saturnin full round using SR_sheet instead of SR_slice
% abcd → cdab   and   inverse cdab → abcd
% ============================================================

function int: bool2int(bool: b) = if b then 1 else 0 endif;

set of int: N = 0..7;
set of int: B = 0..3;

array[N,B] of var bool: state_in;
array[N,B] of var bool: after_s1;
array[N,B] of var bool: after_mds1;
array[N,B] of var bool: after_s2;
array[N,B] of var bool: after_sr;
array[N,B] of var bool: after_mds2;
array[N,B] of var bool: after_inv_sr;

array[0..15] of int: sbox_table = array1d(0..15,
    [0,6,14,1,15,4,7,13,9,8,12,5,2,10,3,11]
);

array[0..7,0..7] of int: M =
    array2d(0..7,0..7, [
        1,1,1,0,1,0,1,0,
        1,0,0,1,0,1,0,1,
        1,0,1,1,0,1,0,0,
        0,1,1,0,1,1,0,0,
        1,0,1,0,1,1,1,0,
        0,1,0,1,1,0,0,1,
        0,1,0,0,1,0,1,1,
        1,1,0,0,0,1,1,0
    ]);

predicate mds_layer(array[0..7,0..3] of var bool: in_bits,
                    array[0..7,0..3] of var bool: out_bits) =
    forall(b in B, i in N)(
        bool2int(out_bits[i,b]) =
            sum(j in N where M[i,j]=1)(bool2int(in_bits[j,b])) mod 2
    );

% ---------- S-box layer ----------
predicate sbox_layer(
    array[0..7,0..3] of var bool: state_in,
    array[0..7,0..3] of var bool: state_out,
    array[0..7] of var bool: active_out
) =
    let {
        array[0..7,0..3] of var bool: sbox_in_bits,
        array[0..7] of var 0..15: sbox_in,
        array[0..7] of var 0..15: sbox_out,
        array[0..7,0..3] of var bool: sbox_out_bits
    } in (
        forall(j in 0..3)(
            sbox_in_bits[0,j]=state_in[j,3] /\
            sbox_in_bits[1,j]=state_in[4+j,3] /\
            sbox_in_bits[2,j]=state_in[j,2] /\
            sbox_in_bits[3,j]=state_in[4+j,2] /\
            sbox_in_bits[4,j]=state_in[j,1] /\
            sbox_in_bits[5,j]=state_in[4+j,1] /\
            sbox_in_bits[6,j]=state_in[j,0] /\
            sbox_in_bits[7,j]=state_in[4+j,0]
        ) /\
        forall(i in N)(
            sbox_in[i]=sum(j in B)(bool2int(sbox_in_bits[i,j])*2^(3-j))
        ) /\
        forall(i in N)(
            active_out[i]<->(sbox_in[i]!=0)
        ) /\
        exists(i in N)(sbox_in[i]!=0) /\
        forall(i in N)(
            sbox_out[i]=sbox_table[sbox_in[i]]
        ) /\
        forall(i in N, j in B)(
            sbox_out_bits[i,j]=((sbox_out[i] div (2^(3-j))) mod 2=1)
        ) /\
        forall(j in 0..3)(
            state_out[j,3]=sbox_out_bits[0,j] /\
            state_out[4+j,3]=sbox_out_bits[1,j] /\
            state_out[j,2]=sbox_out_bits[2,j] /\
            state_out[4+j,2]=sbox_out_bits[3,j] /\
            state_out[j,1]=sbox_out_bits[4,j] /\
            state_out[4+j,1]=sbox_out_bits[5,j] /\
            state_out[j,0]=sbox_out_bits[6,j] /\
            state_out[4+j,0]=sbox_out_bits[7,j]
        )
    );

% ---------- SR_sheet (abcd -> cdab) ----------
predicate sr_sheet(
    array[0..7,0..3] of var bool: in_bits,
    array[0..7,0..3] of var bool: out_bits
) =
    forall(i in 0..3, b in 0..3)(out_bits[i,b] = in_bits[i,b]) /\
    forall(i in 4..7)(
        out_bits[i,3] = in_bits[i,1] /\
        out_bits[i,2] = in_bits[i,0] /\
        out_bits[i,1] = in_bits[i,3] /\
        out_bits[i,0] = in_bits[i,2]
    );

% ---------- inv_SR_sheet (cdab -> abcd) ----------
predicate inv_sr_sheet(
    array[0..7,0..3] of var bool: in_bits,
    array[0..7,0..3] of var bool: out_bits
) =
    forall(i in 0..3, b in 0..3)(out_bits[i,b] = in_bits[i,b]) /\
    forall(i in 4..7)(
        out_bits[i,3] = in_bits[i,1] /\
        out_bits[i,2] = in_bits[i,0] /\
        out_bits[i,1] = in_bits[i,3] /\
        out_bits[i,0] = in_bits[i,2]
    );

% ---------- Flow ----------
array[N] of var bool: active1;
array[N] of var bool: active2;
array[N] of var bool: active_final;

constraint sbox_layer(state_in, after_s1, active1);
constraint mds_layer(after_s1, after_mds1);
constraint sbox_layer(after_mds1, after_s2, active2);
constraint sr_sheet(after_s2, after_sr);
constraint mds_layer(after_sr, after_mds2);
constraint inv_sr_sheet(after_mds2, after_inv_sr);

predicate count_sbox_inputs(
    array[0..7,0..3] of var bool: state_bits,
    array[0..7] of var bool: active_flags
) =
    let {
        array[0..7,0..3] of var bool: sbox_in_bits,
        array[0..7] of var 0..15: sbox_in
    } in (
        forall(j in 0..3)(
            sbox_in_bits[0,j]=state_bits[j,3] /\
            sbox_in_bits[1,j]=state_bits[4+j,3] /\
            sbox_in_bits[2,j]=state_bits[j,2] /\
            sbox_in_bits[3,j]=state_bits[4+j,2] /\
            sbox_in_bits[4,j]=state_bits[j,1] /\
            sbox_in_bits[5,j]=state_bits[4+j,1] /\
            sbox_in_bits[6,j]=state_bits[j,0] /\
            sbox_in_bits[7,j]=state_bits[4+j,0]
        ) /\
        forall(i in N)(
            sbox_in[i]=sum(j in B)(bool2int(sbox_in_bits[i,j])*2^(3-j))
        ) /\
        forall(i in N)(
            active_flags[i]<->(sbox_in[i]!=0)
        )
    );

constraint count_sbox_inputs(after_inv_sr, active_final);

solve minimize sum(i in N)(bool2int(active1[i]));

output [
    "=== Toy Saturnin (SR_sheet version) ===\n\n",

    "Input state (x0..x7, 4 bits each):\n",
    show([if state_in[i,j] then 1 else 0 endif | i in N, j in B]), "\n\n",

    "State after 1st S-box layer:\n",
    show([if after_s1[i,j] then 1 else 0 endif | i in N, j in B]), "\n\n",

    "State after 1st MDS layer:\n",
    show([if after_mds1[i,j] then 1 else 0 endif | i in N, j in B]), "\n\n",

    "State after 2nd S-box layer:\n",
    show([if after_s2[i,j] then 1 else 0 endif | i in N, j in B]), "\n\n",

    "State after SR_sheet:\n",
    show([if after_sr[i,j] then 1 else 0 endif | i in N, j in B]), "\n\n",

    "State after 2nd MDS layer:\n",
    show([if after_mds2[i,j] then 1 else 0 endif | i in N, j in B]), "\n\n",

    "State after inverse SR_sheet (final):\n",
    show([if after_inv_sr[i,j] then 1 else 0 endif | i in N, j in B]), "\n\n",

    "------------------------------------\n",
    "Active S-boxes after 1st S-box layer: ", show(sum(i in N)(bool2int(active1[i]))), "\n",
    "Active S-boxes after 2nd S-box layer: ", show(sum(i in N)(bool2int(active2[i]))), "\n",
    "Active S-boxes after final step: ", show(sum(i in N)(bool2int(active_final[i]))), "\n",
    "Final active flags: ", show([if active_final[i] then 1 else 0 endif | i in N]), "\n"
];

