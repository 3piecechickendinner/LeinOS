import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    createColumnHelper,
    flexRender,
    getCoreRowModel,
    useReactTable,
    getSortedRowModel,
    getFilteredRowModel,
} from '@tanstack/react-table';
import { ArrowUpDown, Search, Filter } from 'lucide-react';
import apiClient from '../../api/client';
import { useVertical } from '../../context/VerticalContext';

const columnHelper = createColumnHelper();

export default function AssetTable() {
    const navigate = useNavigate();
    const { currentVertical } = useVertical();
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [globalFilter, setGlobalFilter] = useState('');
    const [sorting, setSorting] = useState([]);

    useEffect(() => {
        fetchData();
    }, [currentVertical]);

    async function fetchData() {
        setLoading(true);
        try {
            let result;
            if (currentVertical === 'tax_lien') {
                result = await apiClient.getLiens();
            } else if (currentVertical === 'civil_judgment') {
                result = await apiClient.listJudgments();
            } else if (currentVertical === 'probate') {
                result = await apiClient.listProbate();
            } else if (currentVertical === 'mineral_right') {
                result = await apiClient.listMinerals();
            } else {
                result = await apiClient.listSurplus();
            }
            setData(result || []);
        } catch (error) {
            console.error('Failed to fetch assets:', error);
            setData([]);
        } finally {
            setLoading(false);
        }
    }

    const columns = React.useMemo(() => {
        if (currentVertical === 'tax_lien') {
            return [
                columnHelper.accessor('certificate_number', {
                    header: 'Certificate #',
                    cell: info => <span className="font-medium text-slate-900">{info.getValue()}</span>,
                }),
                columnHelper.accessor('county', {
                    header: 'County',
                }),
                columnHelper.accessor('interest_rate', {
                    header: 'Interest %',
                    cell: info => `${info.getValue()}%`,
                }),
                columnHelper.accessor('purchase_amount', {
                    header: 'Amount',
                    cell: info => `$${info.getValue().toLocaleString()}`,
                }),
                columnHelper.accessor('redemption_deadline', {
                    header: 'Deadline',
                    cell: info => new Date(info.getValue()).toLocaleDateString(),
                }),
                columnHelper.accessor('status', {
                    header: 'Status',
                    cell: info => (
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${info.getValue() === 'active' || info.getValue() === 'ACTIVE'
                            ? 'bg-green-50 text-green-700 ring-green-600/20'
                            : 'bg-gray-50 text-gray-600 ring-gray-500/10'
                            }`}>
                            {info.getValue().toUpperCase()}
                        </span>
                    ),
                }),
            ];
        } else if (currentVertical === 'civil_judgment') {
            return [
                columnHelper.accessor('case_number', {
                    header: 'Case #',
                    cell: info => <span className="font-medium text-slate-900">{info.getValue()}</span>,
                }),
                columnHelper.accessor('court_name', {
                    header: 'Court',
                }),
                columnHelper.accessor('defendant_name', {
                    header: 'Debtor Name',
                }),
                columnHelper.accessor('judgment_amount', {
                    header: 'Judgment Amount',
                    cell: info => `$${info.getValue().toLocaleString()}`,
                }),
                columnHelper.accessor('judgment_date', {
                    header: 'Date',
                    cell: info => new Date(info.getValue()).toLocaleDateString(),
                }),
                columnHelper.accessor('status', {
                    header: 'Status',
                    cell: info => (
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${info.getValue() === 'ACTIVE'
                            ? 'bg-green-50 text-green-700 ring-green-600/20'
                            : 'bg-gray-50 text-gray-600 ring-gray-500/10'
                            }`}>
                            {info.getValue().toUpperCase()}
                        </span>
                    ),
                }),
            ];
        } else if (currentVertical === 'probate') {
            return [
                columnHelper.accessor('deceased_name', {
                    header: 'Deceased Name',
                    cell: info => <span className="font-medium text-slate-900">{info.getValue()}</span>,
                }),
                columnHelper.accessor('date_of_death', {
                    header: 'Date of Death',
                    cell: info => new Date(info.getValue()).toLocaleDateString(),
                }),
                columnHelper.accessor('county', {
                    header: 'County',
                }),
                columnHelper.accessor('case_status', {
                    header: 'Case Status',
                    cell: info => (
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${info.getValue() === 'Open' || info.getValue() === 'OPEN'
                            ? 'bg-green-50 text-green-700 ring-green-600/20'
                            : 'bg-gray-50 text-gray-600 ring-gray-500/10'
                            }`}>
                            {info.getValue().toUpperCase()}
                        </span>
                    ),
                }),
            ];
        } else if (currentVertical === 'mineral_right') {
            return [
                columnHelper.accessor('legal_description', {
                    header: 'Legal Description',
                    cell: info => <span className="font-medium text-slate-900">{info.getValue()}</span>,
                }),
                columnHelper.accessor('net_mineral_acres', {
                    header: 'Net Acres',
                    cell: info => info.getValue(),
                }),
                columnHelper.accessor('operator_name', {
                    header: 'Operator',
                }),
                columnHelper.accessor('county', {
                    header: 'County',
                }),
            ];
        } else {
            return [
                columnHelper.accessor('surplus_amount', {
                    header: 'Surplus Amount',
                    cell: info => `$${info.getValue().toLocaleString()}`,
                }),
                columnHelper.accessor('claim_deadline', {
                    header: 'Claim Deadline',
                    cell: info => new Date(info.getValue()).toLocaleDateString(),
                }),
                columnHelper.accessor('county', {
                    header: 'County',
                }),
                columnHelper.accessor('status', {
                    header: 'Status',
                    cell: info => (
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${info.getValue() === 'ACTIVE'
                            ? 'bg-green-50 text-green-700 ring-green-600/20'
                            : 'bg-gray-50 text-gray-600 ring-gray-500/10'
                            }`}>
                            {info.getValue().toUpperCase()}
                        </span>
                    ),
                }),
            ];
        }
    }, [currentVertical]);

    const table = useReactTable({
        data,
        columns,
        state: {
            globalFilter,
            sorting,
        },
        onGlobalFilterChange: setGlobalFilter,
        onSortingChange: setSorting,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
    });

    if (loading) {
        return <div className="p-8 text-center text-slate-500">Loading assets...</div>;
    }

    return (
        <div className="bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl">
            {/* Toolbar */}
            <div className="border-b border-gray-200 px-4 py-4 sm:px-6">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="relative max-w-sm flex-1">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                            <Search className="h-4 w-4 text-gray-400" />
                        </div>
                        <input
                            type="text"
                            value={globalFilter ?? ''}
                            onChange={e => setGlobalFilter(e.target.value)}
                            className="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                            placeholder={`Search ${currentVertical === 'tax_lien' ? 'liens' : currentVertical === 'civil_judgment' ? 'judgments' : currentVertical === 'probate' ? 'probate' : currentVertical === 'mineral_right' ? 'minerals' : 'surplus'}...`}
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="inline-flex items-center gap-2 rounded-md bg-white px-3 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                            <Filter className="h-4 w-4 text-gray-500" />
                            Filter
                        </button>
                    </div>
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                        {table.getHeaderGroups().map(headerGroup => (
                            <tr key={headerGroup.id}>
                                {headerGroup.headers.map(header => (
                                    <th
                                        key={header.id}
                                        scope="col"
                                        className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer hover:bg-gray-100"
                                        onClick={header.column.getToggleSortingHandler()}
                                    >
                                        <div className="flex items-center gap-2">
                                            {flexRender(header.column.columnDef.header, header.getContext())}
                                            <ArrowUpDown className="h-3 w-3 text-gray-400" />
                                        </div>
                                    </th>
                                ))}
                                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                                    <span className="sr-only">Actions</span>
                                </th>
                            </tr>
                        ))}
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                        {table.getRowModel().rows.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length + 1} className="px-3 py-8 text-center text-sm text-gray-500">
                                    No assets found.
                                </td>
                            </tr>
                        ) : (
                            table.getRowModel().rows.map(row => (
                                <tr
                                    key={row.id}
                                    onClick={() => currentVertical === 'tax_lien' && navigate(`/liens/${row.original.id}`)}
                                    className={currentVertical === 'tax_lien' ? 'cursor-pointer hover:bg-gray-50' : ''}
                                >
                                    {row.getVisibleCells().map(cell => (
                                        <td key={cell.id} className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </td>
                                    ))}
                                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                                        <button className="text-blue-600 hover:text-blue-900">
                                            View<span className="sr-only">, {row.original.id}</span>
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
