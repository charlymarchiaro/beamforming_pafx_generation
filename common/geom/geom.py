from .vector_2d import Vector2d, add, dot_prod

ZERO_THRES = 0.001


def are_vectors2d_on_same_half_plane(vectors: list[Vector2d]) -> bool:
    # Two or fewer vectors are always in the same half-plane
    if len(vectors) <= 2:
        return True

    # Get the sum of all vectors
    v_sum = Vector2d(0, 0)
    for v in vectors:
        v_sum = add(v_sum, v)

    # If the sum is zero, then the vectors are not in the same half-plane
    if abs(v_sum.x) < ZERO_THRES and abs(v_sum.y) < ZERO_THRES:
        return False

    # If at least one forms an angle greater than 90° with
    # the sum, then they are not in the same half-plane
    for v in vectors:
        if dot_prod(v_sum, v) < 0:
            return False

    return True


def get_angle_range_boundaries(vectors: list[Vector2d]) -> tuple[int, int]:
    if len(vectors) < 1:
        raise 'The minimum number of vectors to consider is one'

    # Only one vector --> it's both angle range start and end
    if len(vectors) == 1:
        return 0, 0

    min_dot_prod = 1.0
    range_v1_index = 0
    range_v2_index = 0

    for i1, v1 in enumerate(vectors):
        for i2, v2 in enumerate(vectors):
            dot_prod_12 = dot_prod(v1, v2)
            if dot_prod_12 < min_dot_prod:
                min_dot_prod = dot_prod_12
                range_v1_index = i1
                range_v2_index = i2

    v1 = vectors[range_v1_index]
    v2 = vectors[range_v2_index]

    det = v1.x * v2.y - v1.y * v2.x

    return (range_v1_index, range_v2_index) if det > 0 \
        else (range_v2_index, range_v1_index)
