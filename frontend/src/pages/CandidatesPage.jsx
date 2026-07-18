import { flexRender, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, getSortedRowModel, useReactTable } from "@tanstack/react-table";
import { ChevronDown, ChevronLeft, ChevronRight, Download, Filter, MoreHorizontal, Search } from "lucide-react";
import { Fragment } from "react";
import { useMemo, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import { ConfidenceBadge, ScoreBadge, StatusBadge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { SegmentedScore } from "../components/ui/Progress";
import { useAppData } from "../hooks/useAppData";

export default function CandidatesPage() {
  const [globalFilter, setGlobalFilter] = useState("");
  const [expanded, setExpanded] = useState(null);
  const { candidates } = useAppData();
  const exportCandidates = () => {
    const rows = table.getFilteredRowModel().rows.map((row) => row.original);
    const headers = ["name", "role", "college", "score", "confidence", "status", "email", "phone", "degree", "cgpa", "skills"];
    const csvRows = [
      headers.join(","),
      ...rows.map((candidate) => headers.map((header) => csvValue(
        header === "skills" ? candidate.skills.join("; ") : candidate[header],
      )).join(",")),
    ];
    const blob = new Blob([`\uFEFF${csvRows.join("\r\n")}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "candidate_shortlist.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };
  const columns = useMemo(() => [
    { accessorKey: "name", header: "Candidate" },
    { accessorKey: "role", header: "Role" },
    { accessorKey: "college", header: "College" },
    { accessorKey: "score", header: "Score", cell: ({ getValue }) => (typeof getValue() === "number" ? <ScoreBadge score={getValue()} /> : <span className="muted">N/A</span>) },
    { accessorKey: "confidence", header: "Confidence", cell: ({ getValue }) => <ConfidenceBadge value={getValue()} /> },
    { accessorKey: "status", header: "Status", cell: ({ getValue }) => <StatusBadge tone={getValue() === "Shortlist" ? "completed" : getValue() === "Reserve" ? "medium" : "low"}>{getValue()}</StatusBadge> },
    { id: "actions", header: "", cell: ({ row }) => <button className="icon-button" onClick={() => setExpanded(expanded === row.original.id ? null : row.original.id)} type="button"><MoreHorizontal size={18} /></button> },
  ], [expanded]);
  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data: candidates,
    columns,
    state: { globalFilter },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <>
      <PageHeader
        actions={<button className="button primary" disabled={!candidates.length} onClick={exportCandidates} type="button"><Download size={16} /> Export</button>}
        description="Review, filter, sort, and inspect deterministic candidate matches."
        title="All Candidates"
      />
      <Card>
        <div className="card__header" style={{ position: "sticky", top: 0, zIndex: 4 }}>
          <label className="search" style={{ display: "block" }}>
            <Search />
            <input className="input" onChange={(event) => setGlobalFilter(event.target.value)} placeholder="Search candidates..." value={globalFilter} />
          </label>
          <div className="topbar__actions">
            <select className="select" style={{ width: 150 }}><option>Confidence</option></select>
            <select className="select" style={{ width: 150 }}><option>Score Range</option></select>
            <button className="button secondary" type="button"><Filter size={16} /> More Filters</button>
          </div>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id} onClick={header.column.getToggleSortingHandler()}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() ? <ChevronDown size={14} /> : null}
                      </span>
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <Fragment key={row.id}>
                <tr>
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                    ))}
                  </tr>
                  {expanded === row.original.id ? (
                    <tr key={`${row.id}-expanded`}>
                      <td colSpan={columns.length}>
                        <div className="grid two">
                          <div>
                            <strong>{row.original.email}</strong>
                            <p className="muted">{row.original.degree} · CGPA {row.original.cgpa}</p>
                          </div>
                          <div>
                            {typeof row.original.score === "number" ? <SegmentedScore value={row.original.score} /> : <p className="page-copy">Backend upload response does not include scoring data.</p>}
                            <div className="topbar__actions" style={{ marginTop: 10, flexWrap: "wrap" }}>
                              {row.original.skills.map((skill) => <span className="badge medium" key={skill}>{skill}</span>)}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ) : null}
                </Fragment>
              ))}
              {!table.getRowModel().rows.length ? (
                <tr>
                  <td colSpan={columns.length}>No candidates loaded. Upload resumes to populate the table from backend responses.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
        <div className="card__header">
          <span className="muted">Showing {table.getRowModel().rows.length} of {table.getFilteredRowModel().rows.length} candidates</span>
          <div className="topbar__actions">
            <select
              className="select"
              onChange={(event) => table.setPageSize(Number(event.target.value))}
              style={{ width: 120 }}
              value={table.getState().pagination.pageSize}
            >
              {[10, 25, 50, 100].map((pageSize) => (
                <option key={pageSize} value={pageSize}>{pageSize} rows</option>
              ))}
            </select>
            <button className="icon-button" disabled={!table.getCanPreviousPage()} onClick={() => table.previousPage()} type="button"><ChevronLeft size={16} /></button>
            <button className="button secondary" type="button">{table.getState().pagination.pageIndex + 1} / {table.getPageCount() || 1}</button>
            <button className="icon-button" disabled={!table.getCanNextPage()} onClick={() => table.nextPage()} type="button"><ChevronRight size={16} /></button>
          </div>
        </div>
      </Card>
    </>
  );
}

function csvValue(value) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}
