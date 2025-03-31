
    SELECT 
        o.razao_social,
        o.registro_ans,
        strftime('%Y', dc.data_trimestre) as ano,
        ABS(SUM(dc.valor)) as total_despesa
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        operadoras o ON dc.registro_ans = o.registro_ans
    WHERE 
        dc.descricao_conta LIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
        AND strftime('%Y', dc.data_trimestre) = strftime('%Y', (SELECT MAX(data_trimestre) FROM demonstracoes_contabeis))
    GROUP BY 
        o.razao_social, o.registro_ans
    ORDER BY 
        total_despesa DESC
    LIMIT 10
    