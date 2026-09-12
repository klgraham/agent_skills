# Graph snapshot layouts

Use for graph or vector-index storage, not every mmap project.

## Public IDs vs Dense Internal Indices

For mmap-friendly graph/vector indexes, do not let caller-facing IDs double as array indices unless the public API explicitly requires dense `0..n-1` IDs. Split identity into two types:

```zig
pub const ExternalId = u32; // caller-facing, serialized, returned by search
pub const NodeIndex = u32;  // dense internal index: 0..node_count-1
```

Use `NodeIndex` for all flat-array indexing and graph topology:

- `vector_offsets.items[node_index]`
- `edge_offsets.items[node_index]`
- `edge_lengths.items[node_index]`
- edge lists storing neighbor `NodeIndex` values
- entry points and layer/search candidates

Store the caller ID only at API boundaries and metadata:

```zig
pub const NodeMeta = struct {
    external_id: ExternalId,
    level: u8,
    vector_offset: u32,
};
```

For mutable indexes, keep a map in the top-level index, not in the graph core:

```zig
external_to_internal: std.AutoHashMapUnmanaged(ExternalId, NodeIndex),
```

Insert pattern:

1. Reject duplicate external IDs: `if (map.contains(id)) return error.DuplicateExternalId;`
2. Allocate `node_index = graph.nodeCount()`.
3. Append vector data and `vector_offsets[node_index]`.
4. Insert graph metadata with both `node_index` and `external_id`.
5. Put `external_id -> node_index` in the map.
6. Use only `node_index` from this point inward.

Search pattern:

1. Layer/search candidates carry `node_index`, not `id`.
2. Compute distances through `vector_offsets.items[node_index]`.
3. Convert back at the API boundary: `SearchHit.id = graph.node_data.items[node_index].external_id`.

Regression tests should use sparse external IDs, e.g. insert `100`, `5000`, `42`, search near `5000`, and assert returned ID `5000`. Add a duplicate-ID test expecting `error.DuplicateExternalId`.

Serialization can keep the compact metadata record if `ExternalId` remains `u32`; write `external_id` in the node metadata table and rebuild the runtime hash map on mutable load if needed.

## HNSW / Multi-Layer Graph Edge Storage

For HNSW-like mmap graph indexes, node `level` metadata is not topology. The edge identity is:

```text
(level, source_node) -> [destination_node...]
```

Do not implement a single `getEdges(node)` graph and pass `level` through call sites while ignoring it. That creates a single-layer graph with random node levels, not HNSW.

Minimal mutable construction layout:

```zig
pub const EdgeList = std.ArrayListUnmanaged(NodeIndex);
pub const LayerAdjacency = std.ArrayListUnmanaged(EdgeList);

construction_layers: std.ArrayListUnmanaged(LayerAdjacency), // [level][node]
edge_offsets: std.ArrayListUnmanaged(u32),                   // compact slot table
edge_lengths: std.ArrayListUnmanaged(u32),
edge_data: std.ArrayListUnmanaged(NodeIndex),
```

Public graph APIs should require a layer so incorrect callers fail at compile time:

```zig
pub fn getEdges(self: *const Self, level: u8, node_index: NodeIndex) []const NodeIndex
pub fn addEdge(self: *Self, level: u8, src: NodeIndex, dst: NodeIndex) !void
pub fn addBidirectionalEdge(self: *Self, level: u8, a: NodeIndex, b: NodeIndex) !void
pub fn hasEdge(self: *const Self, level: u8, src: NodeIndex, dst: NodeIndex) bool
```

Compact with rectangular slots:

```zig
slot = @as(usize, level) * @as(usize, node_count) + @as(usize, node_index);
```

Snapshot format implications:
- Add `layer_count` to the file header and bump format `version`.
- Size edge offset/length tables as `node_count * layer_count`, not `node_count`.
- Empty `(level,node)` slots are fine: offset points at current `edge_data.len`, length is `0`.
- `isCompacted()` should validate every slot and reject any edge where either endpoint has `NodeMeta.level < level`.
- Tests must prove level separation directly: an edge at layer 0 must not appear at layer 1.


An integer alias does not create a distinct Zig type. Use a wrapper when the compiler must prevent mixing public IDs and dense indices. Apply checked multiplication to slot calculations and roll back all affected containers on insertion failure.
