# account/services/home_service.py
from transactions.models import Transaction


def build_home_context():
    qs = Transaction.objects.exclude(source_file="")

    total_transactions = qs.count()

    source_files = qs.values_list("source_file", flat=True)

    months = []
    for sf in source_files:
        sf = (sf or "").strip()
        yyyymm = sf[:6]
        if len(yyyymm) == 6 and yyyymm.isdigit():
            months.append(yyyymm)

    period_start = None
    period_end = None

    if months:
        months_sorted = sorted(set(months))
        period_start = f"{months_sorted[0][:4]}-{months_sorted[0][4:6]}"
        period_end = f"{months_sorted[-1][:4]}-{months_sorted[-1][4:6]}"

    return {
        "total_transactions": total_transactions,
        "period_start": period_start,
        "period_end": period_end,
    }