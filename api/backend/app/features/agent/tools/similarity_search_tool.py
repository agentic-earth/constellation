import asyncio
import nest_asyncio
from langchain.tools import StructuredTool
from backend.app.features.core.services.block_service import BlockService
from langchain.tools import BaseTool
from typing import List, Dict, Any


async def similarity_search(
    vector: List[float], top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Searches for the most similar paper to the user's query and provides a summary.
    """
    block_service = BlockService()
    vectors = await block_service.search_blocks_by_vector_similarity(vector, top_k)
    return vectors


SimilaritySearchTool = StructuredTool.from_function(
    func=similarity_search,
    name="SimilaritySearchTool",
    description="Searches for the most similar paper to the user's query and provides a summary.",
)

if __name__ == "__main__":
    # Test the tool
    vector = [-0.002615734003484249, -0.009828017093241215, -0.002199068432673812, -0.02003963105380535, 0.013015839271247387, 0.015304192900657654, -0.025132210925221443, 0.007777757477015257, -0.008247333578765392, -0.010641506873071194, 0.012301555834710598, 0.006712945643812418, -0.01514546386897564, 0.03341261297464371, -0.012751289643347263, 0.0011028411099687219, 0.04201047495007515, -0.016997311264276505, 0.023439092561602592, -0.009788334369659424, -0.008372994139790535, 0.02907399833202362, 0.016865035519003868, -0.002238750923424959, -0.009074050933122635, -0.007870350033044815, 0.020092541351914406, -0.032645419239997864, -0.010972193442285061, 0.0047718132846057415, 0.02476184070110321, -0.02165338397026062, -0.004649458918720484, -0.014933823607861996, -0.014523771591484547, -0.028200985863804817, 0.0019064104417338967, -0.010998648591339588, 0.005641520023345947, -0.03161367401480675, -0.004999986849725246, -0.0172354057431221, -0.0012037005508318543, -0.01163356751203537, 0.00030753889586776495, 0.025013163685798645, 0.013954990543425083, -0.004871019162237644, -0.02287031151354313, 0.0172354057431221, 0.017605774104595184, 0.04277766868472099, -0.02596554160118103, -0.007281727157533169, -0.016759216785430908, 0.023611050099134445, -0.01874333806335926, 0.011567430570721626, 0.007334636989980936, -0.02796289138495922, -0.008002624846994877, -0.0023495310451835394, -0.023200998082756996, 0.006878288928419352, -0.010707644745707512, -0.029603097587823868, 0.012063461355865002, 0.011428541503846645, 0.003776445286348462, 0.011441769078373909, 0.032539598643779755, 0.027989346534013748, 0.02145497128367424, -0.01163356751203537, 0.010059498250484467, -6.57240379950963e-05, 0.006418634206056595, -0.01193118654191494, 0.0008126632310450077, 0.0039252545684576035, 0.020290952175855637, -0.0019378256984055042, -0.0005844892584718764, 0.021388834342360497, 0.02276449091732502, -0.004477501846849918, 0.0021775737404823303, 0.018478788435459137, 0.0011044945567846298, 0.014775093644857407, 0.01503964327275753, -0.0027232072316110134, 0.027857070788741112, 0.03970889374613762, -0.048465482890605927, 0.012202349491417408, 0.013075362890958786, 0.00044353390694595873, 0.013915307819843292, -0.024907343089580536, 0.012242032214999199, -0.008736750110983849, -0.025899404659867287, -0.013154728338122368, -0.03679884597659111, -0.03367716073989868, 0.007136224769055843, 0.017910007387399673, 0.025833265855908394, -0.018425878137350082, -0.014708956703543663, 0.039550162851810455, -0.010211613960564137, -0.031058121472597122, 0.021812113001942635, -0.012420603074133396, 0.01784386858344078, 0.02817453071475029, -0.002921619452536106, 0.0027728104032576084, 0.0197486262768507, 0.00041790565592236817, -0.008313470520079136, -0.012790972366929054, 0.0007659537368454039, -0.007149452343583107, -0.023425865918397903, -0.02154756337404251, -0.02566131018102169, -0.0197486262768507, -0.0023396103642880917, 0.011104468256235123, 0.0064583164639770985, 0.004021153785288334, -0.03632265701889992, 0.018994659185409546, -0.013081977143883705, 0.007678551599383354, -0.03730149194598198, 
-0.0065839774906635284, -0.027592521160840988, 0.016322709619998932, -0.024841206148266792, 0.005271150264889002, -0.0044874222949147224, 0.003351512597873807, 0.004474194720387459, 0.03783059120178223, -0.008571406826376915, -0.014470862224698067, -0.004103825427591801, -0.020423227921128273, 9.130060789175332e-05, 0.004120359662920237, -0.004001312423497438, -0.003720228560268879, -0.007499980740249157, 0.0003209730493836105, -0.01752641052007675, -0.013366367667913437, 0.010548914782702923, -0.0299734678119421, 0.007050246465951204, 0.04933849722146988, 0.012519808486104012, -0.00021908011694904417, 0.015502605587244034, 0.002499993424862623, 0.002633921802043915, -0.010707644745707512, 0.0010672921780496836, 0.02326713502407074, -0.017182495445013046, 0.03301578760147095, -0.008055535145103931, 0.03801577538251877, 0.008902093395590782, 0.03931206837296486, 0.0038954925257712603, -0.042275022715330124, -0.01866397261619568, 0.0009341906988993287, 0.0029001247603446245, 0.006898130290210247, -0.00171791878528893, -0.00933198630809784, 0.0026471491437405348, 0.012149439193308353, 0.01785709708929062, -0.008796273730695248, 0.01674598827958107, 0.01855815388262272, -0.004927236121147871, -0.0056944298557937145, -0.6493104696273804, -0.036560751497745514, -0.0040608360432088375, -0.012810813263058662, 0.02435178868472576, -0.005552234128117561, 0.018412651494145393, -0.012056847102940083, -0.015793610364198685, 0.029841192066669464, 0.019312119111418724, 0.0005849025910720229, -0.032857056707143784, -0.019272437319159508, 0.001586470752954483, -0.020793596282601357, 0.00047329574590548873, -0.02386237308382988, 0.031745947897434235, -0.007486753165721893, 0.00038959059747867286, 0.010317433625459671, 0.008538337424397469, 0.010707644745707512, 0.00649469206109643, -0.004785040393471718, 0.003293642308562994, -0.011342563666403294, -0.012043619528412819, 0.015608425252139568, -0.013716896064579487, 0.018822703510522842, 0.0076653240248560905, 0.008009238168597221, 0.0493120402097702, 0.01419308502227068, -0.00747352559119463, 0.01714281365275383, 0.00536374282091856, 0.0299734678119421, -0.012870336882770061, -0.0030340529046952724, 0.021190421655774117, 0.017103129997849464, -0.012354465201497078, 0.03367716073989868, 0.04793638363480568, -0.018386196345090866, 0.005406732205301523, -0.023399410769343376, 0.008062148466706276, 0.011679863557219505, -0.00732140988111496, 0.015383558347821236, 0.019219527021050453, -0.0009978479938581586, 0.012645469978451729, -0.023743323981761932, 0.0019775081891566515, 0.014047582633793354, -0.021428516134619713, 0.0023577981628477573, -0.004451046697795391, -0.02928563952445984, -0.019603123888373375, 0.008955003693699837, -0.0319046787917614, 0.0016120990039780736, 0.0003668558783829212, -0.02835971489548683, -0.014417951926589012, 0.020925872027873993, -0.0022867005318403244, -0.019708944484591484, 0.02518511936068535, -0.0017245325725525618, 0.018306830897927284, 0.004451046697795391, 0.0032655338291078806, 0.010410025715827942, 0.005605144426226616, -0.0011326029198244214, -0.022923221811652184, -0.006008582189679146, 0.0059722065925598145, 0.0022867005318403244, -0.008002624846994877, -0.016481438651680946, 0.004179883282631636, 0.005396811291575432, 0.025515807792544365, 0.015013189055025578, -0.024484064429998398, -0.04343904182314873, 0.011071399785578251, 0.01378303300589323, 0.00571096409112215, 0.013313457369804382, 0.009689128026366234, 0.0033167903311550617, -0.021296240389347076, 0.0043882159516215324, 0.0023032347671687603, 0.0015707631828263402, 0.03370361775159836, -0.013809488154947758, -0.012916632927954197, 0.002129624132066965, 0.029999922960996628, 0.0001567662984598428, -0.0060912542976439, -0.020727459341287613, -0.02626977302134037, -0.010449708439409733, 0.004222872667014599, -0.024933798238635063, 0.00873013585805893, 0.0021180501207709312, 0.008505268953740597, -0.04280412197113037, 0.011018490418791771, 0.004014539998024702, 0.02005285769701004, -0.018121646717190742, 0.005826704669743776, 0.012711606919765472, -0.0017559478292241693, -0.0246560201048851, 0.0012690112926065922, -0.014510544948279858, -0.01053568720817566, 0.011435155756771564, 0.015581970103085041, -0.014722184278070927, 0.02124333195388317, 0.003998005762696266, 0.013650758191943169, 0.0047486647963523865, -0.01703699305653572, 0.010363729670643806, -0.01152113452553749, -0.003994698636233807, -0.004083984065800905, -0.005482790060341358, -0.025608399882912636, -0.0022271766792982817, -0.014259221963584423, 0.011640181764960289, -0.016402073204517365, -0.014497317373752594, -0.004083984065800905, 0.008022465743124485, -0.003898799419403076, 0.013042294420301914, -0.0017675218405202031, -0.0036838529631495476, 0.003465599613264203, -0.0389152429997921, -0.0012012204388156533, -0.03947079926729202, 0.00019458861788734794, 0.01188488956540823, -0.02628300152719021, 0.0025710912887007, -0.006736093666404486, 0.006984109058976173, 0.006015195976942778, -0.002197414869442582, -0.008267174474895, -0.026917919516563416, 0.012116370722651482, -0.032222140580415726, -0.009702355600893497, 0.008452358655631542, -0.001706344773992896, 0.030317382887005806, -0.026706280186772346, -0.016481438651680946, -0.00902114063501358, 0.012724834494292736, 0.0012334624771028757, -0.01152113452553749, -0.015026416629552841, -0.012050233781337738, 0.02197084203362465, -0.012804199941456318, 0.028730085119605064, 0.0038690376095473766, -0.011851821094751358, 0.0316665843129158]
    results = SimilaritySearchTool.run({"vector": vector})
    print(results)