/*
 *    Gianluca Mondini - 2018
 *
 *    Tesi Ing. Informatica - Universita di Pisa
 *
 *    https://github.com/zapateo/Tesi_GianlucaMondini
 */

function RemoveDuplicatedEdges

    input Real[:, 4] edges;

    output Real[:, 4] unique_edges;

protected

    Real [0, 4] empty_unique_edges;
    Boolean insert;

algorithm

    //unique_edges := {{0,2,0,4}, {1,10,1,20}};

    unique_edges := empty_unique_edges;


   // unique_edges := empty_unique_edges;
    for i in 1:size(edges, 1) loop

        insert := true;
        for j in 1:size(unique_edges, 1) loop
            if EdgesAreClose(edges[i], unique_edges[j]) then
                insert := false;
            end if;
        end for;

        if insert then
            unique_edges := cat(1, unique_edges, {edges[i]});
        end if;

    end for;


end RemoveDuplicatedEdges;
