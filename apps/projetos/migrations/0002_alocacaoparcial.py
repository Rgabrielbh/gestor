from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projetos", "0001_initial"),
        ("colaboradores", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlocacaoParcial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("horas_dia", models.DecimalField(decimal_places=1, help_text="Horas diárias dedicadas a este projeto (máx. 8h total)", max_digits=4, verbose_name="horas por dia")),
                ("dt_inicio", models.DateField(verbose_name="data de início")),
                ("dt_fim", models.DateField(blank=True, null=True, verbose_name="data de término")),
                ("observacao", models.TextField(blank=True, verbose_name="observação")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("id_colaborador", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alocacoes_parciais", to="colaboradores.colaborador", verbose_name="colaborador")),
                ("id_alocacao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alocacoes_parciais", to="projetos.colaboradorprojeto", verbose_name="alocação")),
            ],
            options={
                "verbose_name": "alocação parcial",
                "verbose_name_plural": "alocações parciais",
                "ordering": ["-dt_inicio"],
            },
        ),
        migrations.AddIndex(
            model_name="alocacaoparcial",
            index=models.Index(fields=["id_colaborador", "dt_fim"], name="projetos_al_id_cola_idx"),
        ),
    ]
